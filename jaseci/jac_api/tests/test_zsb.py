from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from core.utils.utils import TestCaseHelper
from django.test import TestCase
import uuid
import base64


class test_zsb(TestCaseHelper, TestCase):
    """Test the authorized user node API"""

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            'JSCITfdfdEST_test@jaseci.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.master = self.user.get_master()
        payload = {'op': 'create_graph', 'name': 'Something'}
        res = self.client.post(reverse(f'jac_api:{payload["op"]}'), payload)
        self.gph = self.master._h.get_obj(uuid.UUID(res.data['jid']))
        payload = {'op': 'create_sentinel', 'name': 'Something'}
        res = self.client.post(reverse(f'jac_api:{payload["op"]}'), payload)
        self.snt = self.master._h.get_obj(uuid.UUID(res.data['jid']))
        ll_file = base64.b64encode(
            open("jac_api/tests/zsb.jac").read().encode())
        payload = {'op': 'set_jac_code', 'snt': self.snt.id.urn,
                   'code': ll_file, 'encoded': True}
        res = self.client.post(
            reverse(f'jac_api:{payload["op"]}'), payload, format='json')
        self.run_walker('init', {})

    def tearDown(self):
        super().tearDown()

    def run_walker(self, w_name, ctx, prime=None):
        """Helper to make calls to execute walkers"""
        if(not prime):
            payload = {'snt': self.snt.id.urn, 'name': w_name,
                       'nd': self.gph.id.urn, 'ctx': ctx}
        else:
            payload = {'snt': self.snt.id.urn, 'name': w_name,
                       'nd': prime, 'ctx': ctx}
        res = self.client.post(
            reverse(f'jac_api:prime_run'), payload, format='json')
        return res.data

    def test_zsb_create_answer(self):
        """Test ZSB Create Answer call USE api"""
        data = self.run_walker('add_bot', {'name': "Bot"})
        self.assertEqual(data[0]['kind'], 'bot')
        jid = data[0]['jid']
        data = self.run_walker('create_answer', {'text': "Yep"}, prime=jid)
        self.assertEqual(data[0]['kind'], 'answer')
