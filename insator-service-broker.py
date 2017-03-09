# Importing some necessary libraries
import os                      # to obtain environment info
from flask import Flask,jsonify,request,abort,make_response
from flask_basicauth import BasicAuth
import json
import insator_plans
import service
import requests
# from cloudant import Cloudant


#############################################################
# Database Setup : cloudant nosql db
#############################################################
# db_name = 'insatordb'
# client = None
# db = None

# if 'VCAP_SERVICES' in os.environ:
#     vcap = json.loads(os.getenv('VCAP_SERVICES'))
#     print('Found VCAP_SERVICES')
#     if 'cloudantNoSQLDB' in vcap:
#         creds = vcap['cloudantNoSQLDB'][0]['credentials']
#         user = creds['username']
#         password = creds['password']
#         url = 'https://' + creds['host']
#         client = Cloudant(user, password, url=url, connect=True)
#         db = client.create_database(db_name, throw_on_exists=False)
# elif os.path.isfile('vcap-local.json'):
#     with open('vcap-local.json') as f:
#         vcap = json.load(f)
#         print('Found local VCAP_SERVICES')
#         creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
#         user = creds['username']
#         password = creds['password']
#         url = 'https://' + creds['host']
#         client = Cloudant(user, password, url=url, connect=True)
#         db = client.create_database(db_name, throw_on_exists=False)

#############################################################
# Global Variables
#############################################################

# Start Flask
app = Flask(__name__)

# Which CF Service Broker API version do we support?
X_BROKER_API_VERSION = 2.11
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

# Configure our test username
app.config['BASIC_AUTH_USERNAME'] = 'insator-user'
app.config['BASIC_AUTH_PASSWORD'] = 'insator-pwd'
# Switch off pretty printing of JSON data
app.config['JSONIFY_PRETTYPRINT_REGULAR']=False

basic_auth = BasicAuth(app)

# Some constants we are going to use, save some typing
jsonheaders = {'Content-Type': 'application/json'}
empty_result={}

# Get service information if on Bluemix
if 'VCAP_APPLICATION' in os.environ:
    # get app URL
    service_base=json.loads(os.environ['VCAP_APPLICATION'])['application_uris'][0]
else:
    # we are local, so set service base
    service_base = "localhost:5000"



#############################################################
# Global Variables : Insator Specific
#############################################################

service_dashboard = 'http://www.samsung.com/global/support/globalcontact.html'
# service_dashboard = 'http://fido-ui-service.mybluemix.net'
# service_dashboard = "http://"+service_base+"/my-service//dashboard/"

credentials = {'credentials': { \
        'uri': service_dashboard, \
        'id': 'empty', \
        'apiKey': 'empty', \
      }}

########################################################
# Implement Cloud Foundry Broker API
# In thise file:
# * catalog - return service information including related service plans
# * provision - create the service (add it to the Cloud Foundry / Bluemix catalog)
# * deprovision - delete the service (remove it from the catalog)
# * bind - bind/link a service to an app
# * unbind - remove the linkage to an app
########################################################

#
# Catalog
#
@app.route('/v2/catalog', methods=['GET'])
@basic_auth.required
def catalog():
    # Return the catalog of services handled by this broker
    #
    # GET /v2/catalog:
    #
    # HEADER:
    #     X-Broker-Api-Version: <version>
    #
    # return:
    #     JSON document with details about the
    #     services offered through this broker

    api_version = request.headers.get('X-Broker-Api-Version')
    # Check broker API version
    if not api_version or float(api_version) < X_BROKER_API_VERSION:
        abort(412, "Precondition failed. Missing or incompatible %s. Expecting version %0.1f or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION))
    services={"services": [service.insatorsvc()]}
    return jsonify(services)


#
# Provision
#
@app.route('/v2/service_instances/<instance_id>', methods=['PUT'])
@basic_auth.required
def provision(instance_id):
    # Provision an instance of this service for the org/space
    # as provided in the JSON data
    #
    # PUT /v2/service_instances/<instance_id>:
    #    <instance_id> provided by Bluemix Cloud Controller,
    #   used for future requests like bind, unbind and deprovision
    #
    # BODY:
    #     {
    #       "service_id":        "<service-guid>",
    #       "plan_id":           "<plan-guid>",
    #       "organization_guid": "<org-guid>",
    #       "space_guid":        "<space-guid>"
    #     }
    #
    # return:
    #     JSON document with service details

    if request.headers['Content-Type'] != 'application/json':
        abort(415, 'Unsupported Content-Type: expecting application/json')

    # provision the service by calling out to the service itself
    # not done here to keep the code simple for the tutorial
    
    # get the JSON document in the BODY
    provision_details = request.get_json(force=True)
    print("Provision details : ", provision_details)
    print("In provision instance_id : ", instance_id)

    # if client:
    #     apikey_data = {'API_Key':'1234567890'}
    #     rp_id = {'rp_id':'0987654321'}
    #     db.create_document(apikey_data)
    #     db.create_document(rp_id)
    # else:
    #     print('No database')

    # return basic service information
    new_service = { "dashboard_url": service_dashboard }
    return jsonify(new_service)


#
# Deprovision
#
@app.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@basic_auth.required
def deprovision(instance_id):
    # Deprovision an existing instance of this service
    #
    # DELETE /v2/service_instances/<instance_id>:
    #    <instance_id> is the Cloud Controller provided
    #      value used to provision the instance
    #
    # return:
    #    An empty JSON document is expected

    # deprovision would call the service here
    # not done to keep our code simple for the tutorial

    return jsonify(empty_result)



#
# Bind
#
@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@basic_auth.required
def bind(instance_id, binding_id):
    # Bind an existing instance with the given org and space
    #
    # PUT /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
    #     <instance_id> is the Cloud Controller provided
    #       value used to provision the instance
    #     <binding_id> is provided by the Cloud Controller
    #       and will be used for future unbind requests
    #
    # BODY:
    #     {
    #       "plan_id":           "<plan-guid>",
    #       "service_id":        "<service-guid>",
    #       "app_guid":          "<app-guid>"
    #     }
    #
    # return:
    #     JSON document with credentails and access details
    #     for the service based on this binding
    #     http://docs.cloudfoundry.org/services/binding-credentials.html

    if request.headers['Content-Type'] != 'application/json':
        abort(415, 'Unsupported Content-Type: expecting application/json')

    # get the JSON document in the BODY
    binding_details = request.get_json()
    print("Binding details: " , binding_details)


    # Sample credential
    result={"credentials":     
                {
                  "statusCode": "1200",
                  "id": '4fc8a-b5b1-25fab8b410ee',
                  "status": "ENABLED",
                  "name": "myFakeAppService",
                  "apiKey": '5cf4-4f1f-4b0f-911f-e1d0f1',
                  "statusMessage": "success",
                  "createUserId": "admin"
                }
            }
    return make_response(jsonify(result),201)
        



#
# Unbind
#
@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@basic_auth.required
def unbind(instance_id, binding_id):

    # Unbind an existing instance associated with an app
    #
    # DELETE /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
    #     <instance_id> and <binding_id> are provided by the Cloud Controller
    #
    # return:
    #     An empty JSON document is expected

    return jsonify(empty_result)

########################################################
# Service-related functions for some additional testing
#
#
########################################################

@app.route('/my-service/dashboard/<instance_id>', methods=['GET'])
def dashboard(instance_id):
    # hardcoded HTML, but could be a rendered template, too
    # Consider offering customized page for different instances
    dashboard_page = "<img src='http://contents.dt.co.kr/images/201510/2015102802101860727001[2].jpg' />"
    dashboard_page += "<h3>Welcome!!</h3> You discovered the dashboard for instance : " + instance_id
    dashboard_page += "<img src='http://news.samsungsds.com/wp-content/uploads/2016/10/19-2.jpg' />"
    return dashboard_page


########################################################
# Catch-all section - return HTML page for testing
#
#
########################################################

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    page = '<title>insator Service Broker</title>'
    page += '<h2>This is a sample service broker for Samsung SDS : insator Solution</h2>'
    page += '<p>See for details.</p>'
    page += '<p>You requested path: /%s </p>' % path
    return page


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port),threaded=True)
app.run(host='0.0.0.0', port=int(port),debug=True,threaded=True)


