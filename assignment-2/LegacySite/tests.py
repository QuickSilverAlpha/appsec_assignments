import json.decoder
import os
import io

from django.test import TestCase
from django.test import Client
from LegacySite.models import Card, User

from html import escape

# Create your tests here.

class MyTest(TestCase):
    # Django's test run with an empty database. We can populate it with
    # data by using a fixture. You can create the fixture by running:
    #    mkdir LegacySite/fixtures
    #    python manage.py dumpdata LegacySite > LegacySite/fixtures/testdata.json
    # You can read more about fixtures here:
    #    https://docs.djangoproject.com/en/4.0/topics/testing/tools/#fixture-loading
    fixtures = ["testdata.json"]

    # Assuming that your database had at least one Card in it, this
    # test should pass.
    def test_get_card(self):
        allcards = Card.objects.all()
        self.assertNotEqual(len(allcards), 0)

    def test_xss(self):
        test_client = Client()
        http_resp = test_client.get("/buy?director=<script>alert(\"RA\")</script>")

        '''For RXSS to occur, the javascript should be present in the response. Since the fix escapes the js,
        it should not be present'''
        self.assertNotContains(http_resp, "<script>alert(\"RA\")</script>")

    def test_csrf_get(self):

        test_client = Client(enforce_csrf_checks=True)

        # Performing Login
        get_login_resp = test_client.get("/login.html")
        csrf_token = get_login_resp.context["csrf_token"]
        login_resp = test_client.post("/login.html", {"uname": "roh", "pword": "roh",
                                                      "csrfmiddlewaretoken": csrf_token}, follow=True)

        http_resp = test_client.get("/gift.html?amount=999&username=test2")

        # The above request is an invalid request and hence server throws 400: Bad Request
        self.assertEqual(http_resp.status_code, 400)

    def test_csrf_post(self):
        test_client = Client(enforce_csrf_checks=True)

        # Performing Login
        get_login_resp = test_client.get("/login.html")
        csrf_token = get_login_resp.context["csrf_token"]
        login_resp = test_client.post("/login.html", {"uname": "roh", "pword": "roh",
                                                      "csrfmiddlewaretoken": csrf_token}, follow=True)

        http_resp = test_client.post("/gift/0", {"username": "test2", "amount": "999"})

        # The above request submits the form without the csrf token and hence server throws 403: Forbidden
        self.assertEqual(http_resp.status_code, 403)

    def test_sqli(self):
        test_client = Client()

        # Perform login
        login_resp = test_client.login(username='roh', password='roh')

        with open("part1/sqli.gftcrd", "r") as fd:
            http_resp = test_client.post("/use.html", {'card_supplied': True, "card_fname": "test", "card_data": fd})

            self.assertNotContains(http_resp, "000000000000000000000000000078d2$18821d89de11ab18488fdc0a01f1ddf4d290e19"
                                              "8b0f80cd4974fc031dc2615a3")

    def test_cmdi(self):
        test_client = Client()

        # Perform login
        login_resp = test_client.login(username='roh', password='roh')

        with open("malformed.json", "r") as fd:
            try:
                http_resp = test_client.post("/use.html", {'card_supplied': True, "card_data": fd,
                                                           "card_fname": "bla.txt; touch hacked;"})

            except json.decoder.JSONDecodeError:
                pass

        self.assertNotEqual(os.path.exists("hacked"), True)

    def test_buy_and_use(self):
        client = Client()
        client.login(username='test', password='test')
        user = User.objects.get(username='test')
        response = client.post('/buy/4', {'amount': 1337})
        self.assertEqual(response.status_code, 200)
        # Get the card that was returned
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]
        card_data = response.content
        response = client.post('/use.html',
                               {
                                   'card_supplied': 'True',
                                   'card_fname': 'Test',
                                   'card_data': io.BytesIO(card_data),
                               }
                               )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Card used!', response.content)
        self.assertTrue(Card.objects.get(pk=card.id).used)
