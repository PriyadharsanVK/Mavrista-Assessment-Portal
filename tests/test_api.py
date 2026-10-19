import json
import os
import secrets
import sys
import unittest
from datetime import timedelta
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT))
_data=PROJECT/f'.assessment-tests-{secrets.token_hex(5)}'
_data.mkdir(exist_ok=True)
os.environ['ASSESSMENT_DATA_DIR']=str(_data)
import server

class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.init_db()
        con=server.db()
        con.execute('INSERT INTO users(id,role,name,email,password_hash,created_at) VALUES(?,?,?,?,?,?)',
                    ('ADM-TEST','admin','Test Admin','admin@test.invalid',server.password_hash('correct horse battery staple'),server.stamp()))

    @classmethod
    def tearDownClass(cls):
        pass

    def request(self,method,path,session=None,payload=None):
        handler=object.__new__(server.Handler)
        handler.path=path
        handler.headers={}
        handler.client_address=('127.0.0.1',12345)
        handler.payload=payload or {}
        if session:
            handler.headers.update({'Cookie':session['cookie'],'X-CSRF-Token':session['csrf']})
        handler.read_json=lambda:handler.payload
        try:
            result=handler.api(method,path,{})
            return (*result,None)[:3]
        except server.ApiError as err:
            return err.status,{'error':err.message},None

    def login(self,login,password):
        status,data,cookie=self.request('POST','/api/auth/login',payload={'loginId':login,'password':password})
        self.assertEqual(status,200,data)
        if isinstance(cookie,dict): cookie=cookie.get('Set-Cookie','')
        return {'cookie':cookie.split(';',1)[0],'csrf':data['csrfToken'],'user':data['user']}

    def test_domain_scoped_attempt_autosave_monitoring_and_results(self):
        status,_,_=self.request('GET','/api/admin/domains')
        self.assertEqual(status,401)
        admin=self.login('admin@test.invalid','correct horse battery staple')
        status,data,_=self.request('POST','/api/admin/domains',admin,{'name':'Java Basics','category':'Software','description':'Test domain','icon':'☕'})
        self.assertEqual(status,201,data);domain=data['domain']
        status,mcq,_=self.request('POST','/api/admin/questions',admin,{'domainId':domain['id'],'type':'MCQ','title':'Pick the correct answer','difficulty':'Easy','data':{'options':['A','B'],'correctOption':'B'}})
        self.assertEqual(status,201,mcq)
        coding={'languages':['Python'],'starterCodes':{'Python':'print(input())'},'sampleTests':[{'input':'hi','output':'hi'}],'hiddenTests':[{'input':'hidden','output':'hidden'}],'timeLimitSeconds':2,'memoryLimitMB':128}
        status,code,_=self.request('POST','/api/admin/questions',admin,{'domainId':domain['id'],'type':'Coding','title':'Echo input','difficulty':'Easy','data':coding})
        self.assertEqual(status,201,code)
        status,limited,_=self.request('POST','/api/admin/assessments',admin,{'title':'Pool validation','domainId':domain['id'],'startsAt':server.stamp(server.now_utc()+timedelta(days=1)),'durationMinutes':45,'mcqCount':3,'codingCount':1})
        self.assertEqual(status,400);self.assertIn('published MCQs',limited['error'])
        status,other,_=self.request('POST','/api/admin/domains',admin,{'name':'Other Domain','category':'Electrical / Electronics'})
        self.assertEqual(status,201);other_domain=other['domain']
        other_q={'options':['yes','no'],'correctOption':'A'}
        status,_,_=self.request('POST','/api/admin/questions',admin,{'domainId':other_domain['id'],'type':'MCQ','title':'Other domain item','difficulty':'Easy','data':other_q})
        self.assertEqual(status,201)
        con=server.db();started=server.stamp(server.now_utc()-timedelta(minutes=1));end=server.stamp(server.now_utc()+timedelta(minutes=40))
        con.execute('INSERT INTO assessments(id,domain_id,title,starts_at,duration_min,mcq_count,coding_count,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)',('A-TEST',domain['id'],'Test assessment',started,40,1,1,'Scheduled',server.stamp()))
        con.execute('INSERT INTO assessments(id,domain_id,title,starts_at,duration_min,mcq_count,coding_count,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)',('A-OTHER',other_domain['id'],'Other assessment',started,40,1,0,'Scheduled',server.stamp()))
        con.execute('INSERT INTO users(id,role,name,email,password_hash,domain_id,created_at) VALUES(?,?,?,?,?,?,?)',('ST-TEST','student','Test Student','student@test.invalid',server.password_hash('another correct horse battery'),domain['id'],server.stamp()))
        student=self.login('ST-TEST','another correct horse battery')
        status,home,_=self.request('GET','/api/student/home',student)
        self.assertEqual(status,200);self.assertEqual(home['domain']['id'],domain['id']);self.assertEqual(len(home['assessments']),1)
        status,_,_=self.request('POST','/api/student/attempts/start',student,{'assessmentId':'A-OTHER'})
        self.assertEqual(status,404)
        status,attempt,_=self.request('POST','/api/student/attempts/start',student,{'assessmentId':'A-TEST'})
        self.assertEqual(status,201,attempt);self.assertEqual(len(attempt['questions']),2)
        coding_q=next(q for q in attempt['questions'] if q['type']=='Coding')
        self.assertNotIn('hiddenTests',coding_q);self.assertEqual(coding_q['languages'],['Python'])
        self.assertNotIn('correctOption',next(q for q in attempt['questions'] if q['type']=='MCQ'))
        status,runner,_=self.request('POST',f"/api/student/attempts/{attempt['attempt']['id']}/run",student,{'questionId':coding_q['id'],'language':'Python','code':'print(input())'})
        self.assertEqual(status,503);self.assertIn('runner',runner['error'].lower())
        mcq_q=next(q for q in attempt['questions'] if q['type']=='MCQ')
        status,_,_=self.request('PUT',f"/api/student/attempts/{attempt['attempt']['id']}/answers/{mcq_q['id']}",student,{'answer':{'optionIndex':1}})
        self.assertEqual(status,200)
        status,_,_=self.request('POST',f"/api/student/attempts/{attempt['attempt']['id']}/events",student,{'type':'fullscreen'})
        self.assertEqual(status,200)
        for i in range(1,4):
            status,event,_=self.request('POST',f"/api/student/attempts/{attempt['attempt']['id']}/events",student,{'type':'visibility'})
            self.assertEqual(status,200);self.assertEqual(event['autoSubmitted'],i==3)
        status,closed,_=self.request('GET',f"/api/student/attempts/{attempt['attempt']['id']}",student)
        self.assertEqual(status,200);self.assertEqual(closed['attempt']['status'],'Submitted')
        self.assertEqual(closed['attempt']['score'],1)
        status,_,_=self.request('POST','/api/student/attempts/start',student,{'assessmentId':'A-TEST'})
        self.assertEqual(status,409)
        status,flags,_=self.request('GET','/api/admin/flags',admin)
        self.assertEqual(status,200);self.assertEqual(sum(f['event_type']=='visibility' for f in flags['flags']),3);self.assertEqual(sum(f['event_type']=='fullscreen' for f in flags['flags']),1)
        status,results,_=self.request('GET','/api/admin/results',admin)
        self.assertEqual(status,200);self.assertEqual(results['results'][0]['score'],1)
        status,detail,_=self.request('GET',f"/api/admin/results/{attempt['attempt']['id']}",admin)
        self.assertEqual(status,200)
        mcq_detail=next(x for x in detail['answers'] if x['question']['type']=='MCQ')
        self.assertTrue(mcq_detail['question']['isCorrect'])
        coding_detail=next(x for x in detail['answers'] if x['question']['type']=='Coding')
        self.assertNotIn('hiddenTests',coding_detail['question'])

        # Test Domain PATCH
        status,patched,_=self.request('PATCH',f"/api/admin/domains/{domain['id']}",admin,{'name':'Java Advanced','category':'Software'})
        self.assertEqual(status,200,patched)
        self.assertEqual(patched['domain']['name'],'Java Advanced')

        # Test Student creation with domainId
        status,st_created,_=self.request('POST','/api/admin/students',admin,{'id':'ST-DOMID','name':'Dom Id Student','email':'domid@test.invalid','domainId':domain['id'],'password':'a-long-valid-test-password'})
        self.assertEqual(status,201,st_created)

        # Test Student bulk import
        status,bulk_st,_=self.request('POST','/api/admin/students/bulk',admin,{'students':[
            {'id':'ST-BULK1','name':'Bulk One','email':'b1@test.invalid','domainId':domain['id']},
            {'id':'ST-BULK2','name':'Bulk Two','email':'b2@test.invalid','domain':patched['domain']['name']}
        ]})
        self.assertEqual(status,201,bulk_st)
        self.assertEqual(bulk_st['count'],2)

        # Test Student creation with blank password (auto-generated) and dot in ID
        status,st_auto,_=self.request('POST','/api/admin/students',admin,{'id':'ST.AUTO.01','name':'Auto Pass Student','email':'auto@test.invalid','domainId':domain['id']})
        self.assertEqual(status,201,st_auto)
        self.assertEqual(st_auto['temporaryPassword'],'st.auto.01@2026')

        # Test Student creation with 6-char password
        status,st_short,_=self.request('POST','/api/admin/students',admin,{'id':'ST-SHORT','name':'Short Pass Student','email':'short@test.invalid','domainId':domain['id'],'password':'secret'})
        self.assertEqual(status,201,st_short)

        # Test Sheets config endpoints
        status,cfg,_=self.request('GET','/api/admin/sheets/config',admin)
        self.assertEqual(status,200,cfg)
        status,cfg_save,_=self.request('POST','/api/admin/sheets/config',admin,{'webhookUrl':'https://script.google.com/macros/s/AKfycbxTest/exec'})
        self.assertEqual(status,200,cfg_save)
        self.assertTrue(cfg_save['configured'])

        # Test retention & cleanup endpoints
        status,ret_get,_=self.request('GET','/api/admin/settings/retention',admin)
        self.assertEqual(status,200,ret_get)
        self.assertIn('retentionDays',ret_get)

        status,ret_set,_=self.request('POST','/api/admin/settings/retention',admin,{'retentionDays':60})
        self.assertEqual(status,200,ret_set)
        self.assertEqual(ret_set['retentionDays'],60)

        status,clean_res,_=self.request('POST','/api/admin/cleanup',admin,{})
        self.assertEqual(status,200,clean_res)
        self.assertTrue(clean_res['ok'])
        self.assertIn('deleted',clean_res)

        # Test session inactivity timeout
        con = server.db()
        con.execute("UPDATE sessions SET expires_at=?", (server.stamp(server.now_utc() - timedelta(minutes=35)),))
        status,expired_res,_=self.request('GET','/api/admin/domains',admin)
        self.assertEqual(status,401)
        self.assertIn('inactivity',expired_res.get('error','').lower())

if __name__=='__main__': unittest.main()
