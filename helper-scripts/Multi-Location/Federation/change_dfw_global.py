#!/usr/bin/env python
# Requires Python 3.x
# Author: Thomas Vigneron <tvigneron>
# Additions: Madhukar Krishnarao <madhukark>
# Script to move GM objects under a specific location to the default one.
# This script is neither supported nor endorsed by VMware but meant as an example

import warnings
from json import loads, dumps
from requests import get, patch
from requests.packages.urllib3 import disable_warnings
from requests.auth import HTTPBasicAuth
from copy import deepcopy
from ast import literal_eval
disable_warnings()
warnings.filterwarnings("ignore")

#put your Global Manager IP or FQDN
hostname = "10.114.218.181"

#put your username
username = "admin"

#put your password
password = "VMware1!VMware1!"

#put the list of Region / Locations from which you want to make Global
domains = ["LM-Paris","LM-London"]

#put the security objects you want to make Global. By default it covers groups and Dfw
resource_types =["Domain","SecurityPolicy","Group","Rule"]

class NsxMgr:
    def __init__(self, hostname, username, password, mgr_type = "global", certificate_validation = False):
        self.hostname = str(hostname)
        self.username = str(username)
        self.password = str(password)
        self.certificate_validation = certificate_validation
        self.mgr_type = mgr_type
        self.tree = "/global-infra"
        self.path = "/global-manager/api/v1/global-infra"
        self.url = "https://" + self.hostname + self.path

    def get_conf(self, resource_types = ["Domain","SecurityPolicy","Group","Rule"]):
        """Method to get NSX-T logical configuration leveraging Policy Filters"""
        filter = "?filter=Type-" + "|".join(resource_types)
        uri = self.url + filter
        res = get(  uri,
                    verify = self.certificate_validation,
                    auth = HTTPBasicAuth(self.username, self.password)
                    )
        return res.content.decode()

    def patch_conf(self, body):
        """Method to do patch against NSX-T manager"""
        uri = self.url
        #print(uri)
        headers = {"content-type": "application/json"}
        res = patch(uri,
                    data = body,
                    headers = headers,
                    verify = self.certificate_validation,
                    auth = HTTPBasicAuth(self.username, self.password)
                    )
        return {"status_code" : res.status_code, "response_text" : res.text}

    def identify_changes(self, domains, resource_types = ["Domain","SecurityPolicy","Group","Rule"]):
        """Creates dictionaries per domain with rules to add and delete in
        order to move to the default domain"""
        body = self.get_conf(resource_types)
        body = loads(body)
        infra_children = body["children"]

        change_dict = dict()
        change_dict["default"] = []

        for child in infra_children:
            try:
                domain = child["Domain"]
            except KeyError:
                pass

            if domain["id"] in domains:
                change_dict[domain["id"]] =[]
                #print(domain["id"])
                for domain_child in domain["children"]:
                    for resource_type in resource_types:
                        if resource_type == "Domain":
                            pass
                        else:
                            try:
                                #We create the objects in the new domain
                                default_domain_object = deepcopy(domain_child[resource_type])
                                domain_object = deepcopy(domain_child[resource_type])
                                for domain_to_migrate in domains:
                                    default_domain_object = str(default_domain_object).replace(self.tree  + '/domains/' + domain_to_migrate, self.tree  + '/domains/default')
                                default_domain_object = literal_eval(default_domain_object)

                                change_dict["default"].append({resource_type:default_domain_object, "resource_type" : "Child" + resource_type})

                                #We prepare the deletion of the object under the domain migrated
                                domain_object = domain_child[resource_type]
                                domain_object["marked_for_delete"] = True
                                change_dict[domain["id"]].append({resource_type:domain_object, "resource_type" : "Child" + resource_type, "marked_for_delete":True})

                            except KeyError:
                                pass
        return change_dict

    def generate_body(self, domains, resource_types = ["Domain","SecurityPolicy","Group","Rule"]):
        """Generates the request body to move ChildObjects to default domain."""
        change_dict = self.identify_changes(domains, resource_types)
        body = {        "resource_type": "Infra",
                        "children": []            }

        for domain in change_dict:
            body["children"].append({
                        "resource_type": "ChildResourceReference",
                        "id": domain,
                        "target_type": "Domain",
                        "children": change_dict[domain]
                        }
            )
        body = dumps(body)
        #print(body)
        return body

def ask_confirmation():
    ans = str(input ("Continue with applying the changes? (y/n): ")).lower().strip()
    try:
        if ans[0] == 'y':
            return True
        elif ans[0] == 'n':
            return False
        else:
            print ("Invalid Input")
            return ask_confirmation()
    except Exception as error:
        print ("Please enter valid input")
        print (error)
        return ask_confirmation()


if __name__ == "__main__":
    #Logs against the Global Manager:
    print ("")
    print ("Connecting to Global Manager: %s", hostname)
    gm = NsxMgr(hostname, username, password)
    

    #backup previous firewall configuration:
    file_backup = open("fwll_backup.json","w")
    print ("Gathering existing DFW configuration ...")
    file_backup.write(gm.get_conf(resource_types))
    print ("Writing existing DFW configuration in backup file: fwll_backup.json")

    #generates the configuration creating new objects on default domain, deleting old objects:
    print ("Changing to Global domain for the following resource_types: ", resource_types)
    conf = gm.generate_body(domains, resource_types)
    file_new = open("fwll_new.json","w")
    file_new.write(conf)
    print ("New config written into: fwll_new.json")

    if (ask_confirmation()):
        #Push the new configuration on the Global Manager. This will delete your old objects.
        print ("Applying new configuration. Please wait ...")
        gm.patch_conf(conf)
        print ("Changes applied Successfully!")
    else:
        print ("Exiting without applying changes. New configuration saved in fwll_new.json")
    print ("")

