import httplib, urllib2, time, calendar
from datetime import datetime
from decimal import Decimal
from xml.etree.ElementTree import fromstring
from xml.etree import ElementTree as ET
from base64 import b64encode

API_VERSION = 'v4'

def utc_to_local(dt):
    ''' Converts utc datetime to local'''
    secs = calendar.timegm(dt.timetuple())
    return datetime(*time.localtime(secs)[:6])
    

def str_to_datetime(s):
    ''' Converts ISO 8601 string (2009-11-10T21:11Z) to LOCAL datetime'''
    return utc_to_local(datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'))


class Client:
    def __init__(self, token, site_name):
        self.auth = b64encode('%s:x' % token)
        self.base_host = 'spreedly.com'
        self.base_path = '/api/%s/%s' % (API_VERSION, site_name)
        self.base_url = 'https://%s%s' % (self.base_host, self.base_path)
        self.url = None

    
    def get_response(self):
        return self.response
    
    def get_url(self):
        return self.url
    
    def set_url(self, url):
        self.url = '%s/%s' % (self.base_url, url)
    
    def query(self, data=None, put=False):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        
        req = urllib2.Request(url=self.get_url())
        req.add_header('User-agent', 'python-spreedly 1.0')
        req.add_header('Authorization', 'Basic %s' % self.auth)


        # Convert to POST if we got some data
        if data:
            req.add_header('Content-Type', 'application/xml')
            req.add_data(data)
            
        if put:
            req.get_method = lambda: 'PUT'
        
        f = opener.open(req)
        self.response = f.read()

    
    def get_plans(self):
        self.set_url('subscription_plans.xml')
        self.query()
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscription-plan'):
            data = {
                'name': plan.findtext('name'),
                'description': plan.findtext('description'),
                'terms': plan.findtext('terms'),
                'plan_type': plan.findtext('plan-type'),
                'price': Decimal(plan.findtext('price')),
                'enabled': True if plan.findtext('enabled') == 'true' else False,
                'force_recurring': \
                    True if plan.findtext('force-recurring') == 'true' else False,
                'force_renew': \
                    True if plan.findtext('needs-to-be-renewed') == 'true' else False,
                'duration': int(plan.findtext('duration-quantity')),
                'duration_units': plan.findtext('duration-units'),
                'feature_level': plan.findtext('feature-level'),
                'return_url': plan.findtext('return-url'),
                'version': int(plan.findtext('version')) \
                    if plan.findtext('version') else 0,
                'speedly_id': int(plan.findtext('id')),
                'speedly_site_id': int(plan.findtext('site-id')) \
                    if plan.findtext('site-id') else 0,
                'created_at': str_to_datetime(plan.findtext('created-at')),
                'date_changed': str_to_datetime(plan.findtext('updated-at')),
            }
            result.append(data)
        return result
    
    def create_subscriber(self, customer_id, screen_name):
        '''
        Creates a subscription
        '''
        data = '''
        <subscriber>
            <customer-id>%d</customer-id>
            <screen-name>%s</screen-name>
        </subscriber>
        ''' % (customer_id, screen_name)
        
        self.set_url('subscribers.xml')
        self.query(data)
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'gift': True if plan.findtext('on-gift') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'created_at': str_to_datetime(plan.findtext('created-at')),
                'date_changed': str_to_datetime(plan.findtext('updated-at')),
                'active_until': str_to_datetime(plan.findtext('active-until')) if plan.findtext('active-until') else None,
            }
            
            result.append(data)
        return result[0]
    
    def delete_subscriber(self, id):
        if 'test' in self.base_path:
            headers = {'Authorization': 'Basic %s' % self.auth}
            conn = httplib.HTTPSConnection(self.base_host)
            conn.request(
                'DELETE', '%s/subscribers/%d.xml' % (self.base_path, id),
                '',
                headers
            )
            response = conn.getresponse()
            return response.status
        return
    
    def subscribe(self, subscriber_id, plan_id, trial=False):
        '''
        Subscribe a user to some plan
        '''
        data = '<subscription_plan><id>%d</id></subscription_plan>' % plan_id
        
        if trial:
            self.set_url('subscribers/%d/subscribe_to_free_trial.xml' % subscriber_id)
        
        self.query(data)
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'gift': True if plan.findtext('on-gift') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'created_at': str_to_datetime(plan.findtext('created-at')),
                'date_changed': str_to_datetime(plan.findtext('updated-at')),
                'active_until': str_to_datetime(plan.findtext('active-until')) if plan.findtext('active-until') else None,
            }
            result.append(data)
        return result[0]
    
    def cleanup(self):
        '''
        Removes ALL subscribers. NEVER USE IN PRODUCTION!
        '''
        if 'test' in self.base_path:
            headers = {'Authorization': 'Basic %s' % self.auth}
            conn = httplib.HTTPSConnection(self.base_host)
            conn.request(
                'DELETE', '%s/subscribers.xml' % self.base_path,
                '',
                headers
            )
            response = conn.getresponse()
            return response.status
        return
    
    def get_info(self, subscriber_id):
        self.set_url('subscribers/%d.xml' % subscriber_id)
        self.query('')
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'email': plan.findtext('email'),
                'screen_name': plan.findtext('screen-name'),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'gift': True if plan.findtext('on-gift') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'created_at': str_to_datetime(plan.findtext('created-at')),
                'date_changed': str_to_datetime(plan.findtext('updated-at')),
                'active_until': str_to_datetime(plan.findtext('active-until')) if plan.findtext('active-until') else None,
            }
            result.append(data)
        return result[0]
        
    def set_info(self, subscriber_id, **kw):
        root = ET.Element('subscriber')
        
        for key, value in kw.items():
            e = ET.SubElement(root, key)
            e.text = value
        
        self.set_url('subscribers/%d.xml' % subscriber_id)
        self.query(data=ET.tostring(root), put=True)
        
        
    def create_complimentary_subscription(self, subscriber_id, duration, duration_units, feature_level):
        data = """<complimentary_subscription>
            <duration_quantity>%s</duration_quantity>
            <duration_units>%s</duration_units>
            <feature_level>%s</feature_level>
            </complimentary_subscription>""" % (duration, duration_units, feature_level)
        
        self.set_url('subscribers/%s/complimentary_subscriptions.xml' % subscriber_id)
        self.query(data)
    
    def complimentary_time_extensions(self, subscriber_id, duration, duration_units):
        data = """<complimentary_time_extension>
            <duration_quantity>%s</duration_quantity>
            <duration_units>%s</duration_units>
            </complimentary_time_extension>""" % (duration, duration_units)
        
        self.set_url('subscribers/%s/complimentary_time_extensions.xml' % subscriber_id)
        self.query(data)
    
    def get_or_create_subscriber(self, subscriber_id, screen_name):
        try:
            return self.get_info(subscriber_id)
        except urllib2.HTTPError, e:
            if e.code == 404:
                return self.create_subscriber(subscriber_id, screen_name)
