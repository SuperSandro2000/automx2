import unittest
from typing import List
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ParseError
from xml.etree.ElementTree import fromstring

from automx2.generators.outlook import NS_RESPONSE
from automx2.model import EXAMPLE_COM
from automx2.model import EXAMPLE_NET
from automx2.model import EXAMPLE_ORG
from automx2.model import HORUS_IMAP
from automx2.model import HORUS_SMTP
from automx2.model import SERVERLESS_DOMAIN
from automx2.model import SYS4_MAILSERVER
from automx2.model import sample_server_names
from automx2.server import MSOFT_CONFIG_ROUTE
from automx2.views import CONTENT_TYPE_XML
from tests.base import TestCase
from tests.base import body


class MsRoutes(TestCase):
    @staticmethod
    def response_element(element: Element) -> Element:
        ns = {'n': NS_RESPONSE}
        return element.find('n:Response', ns)

    @staticmethod
    def server_elements(element: Element, server_type: str) -> List[Element]:
        ns = {'n': NS_RESPONSE}
        r = []
        for p in element.findall('n:Response/n:Account/n:Protocol', ns):
            if p.find('n:Type', ns).text == server_type:
                r.append(p.find('n:Server', ns))
        return r

    def imap_server_elements(self, element: Element) -> List[Element]:
        return self.server_elements(element, 'IMAP')

    def smtp_server_elements(self, element: Element) -> List[Element]:
        return self.server_elements(element, 'SMTP')

    def test_ms_empty_post(self):
        with self.app:
            with self.assertRaises(ParseError):
                self.post(MSOFT_CONFIG_ROUTE, data=None, content_type=CONTENT_TYPE_XML)

    def test_ms_partial_post(self):
        with self.app:
            self.post(MSOFT_CONFIG_ROUTE, data='<ham/>', content_type=CONTENT_TYPE_XML)

    def test_ms_no_content_type(self):
        with self.app:
            r = self.post(MSOFT_CONFIG_ROUTE, data='eggs')
            self.assertEqual(400, r.status_code)

    def test_ms_no_domain_match(self):
        with self.app:
            r = self.get_msoft_config('a@b.c')
            self.assertEqual(200, r.status_code)
            self.assertEqual(CONTENT_TYPE_XML, r.mimetype)
            e: Element = fromstring(body(r))
            e = self.response_element(e)
            self.assertIsInstance(e, Element)
            self.assertEqual([], list(e))

    def test_ms_valid_domain(self):
        with self.app:
            r = self.get_msoft_config(f'a@{EXAMPLE_COM}')
            self.assertEqual(200, r.status_code)
            self.assertEqual(CONTENT_TYPE_XML, r.mimetype)
            e: Element = fromstring(body(r))
            self.assertNotEqual([], self.imap_server_elements(e))
            self.assertNotEqual([], self.smtp_server_elements(e))

    def test_ms_imap(self):
        with self.app:
            r = self.get_msoft_config(f'a@{EXAMPLE_ORG}')
            x = self.imap_server_elements(fromstring(body(r)))
            self.assertEqual(sample_server_names['imap2'], x[0].text)

    def test_ms_smtp(self):
        with self.app:
            r = self.get_msoft_config(f'a@{EXAMPLE_NET}')
            x = self.smtp_server_elements(fromstring(body(r)))
            self.assertEqual(sample_server_names['smtp1'], x[0].text)

    def test_domain_without_servers(self):
        with self.app:
            r = self.get_msoft_config(f'a@{SERVERLESS_DOMAIN}')
            b = fromstring(body(r))
            self.assertEqual([], self.imap_server_elements(b))
            self.assertEqual([], self.smtp_server_elements(b))

    def test_horus_imap(self):
        with self.app:
            r = self.get_msoft_config(f'a@horus-it.com')
            b = fromstring(body(r))
            imap = self.imap_server_elements(b)
            self.assertEqual(1, len(imap))
            self.assertEqual(HORUS_IMAP, imap[0].text)

    def test_horus_smtp(self):
        with self.app:
            r = self.get_msoft_config(f'a@horus-it.de')
            b = fromstring(body(r))
            smtp = self.smtp_server_elements(b)
            self.assertEqual(1, len(smtp))
            self.assertEqual(HORUS_SMTP, smtp[0].text)

    def test_sys4_servers(self):
        with self.app:
            r = self.get_msoft_config(f'a@sys4.de')
            b = fromstring(body(r))
            imap = self.imap_server_elements(b)
            self.assertEqual(1, len(imap))
            smtp = self.smtp_server_elements(b)
            self.assertEqual(1, len(smtp))
            self.assertEqual(SYS4_MAILSERVER, imap[0].text)
            self.assertEqual(SYS4_MAILSERVER, smtp[0].text)


if __name__ == '__main__':
    unittest.main()
