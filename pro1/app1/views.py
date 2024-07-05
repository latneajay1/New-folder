from rest_framework import viewsets
from rest_framework.views import APIView
from .models import DefaultPermission, Product
from .serializers import DefaultPermissionSerializer1, DefaultPermissionSerializer2, ProductSerializer
from rest_framework.response import Response
import os
import json
import requests

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class DefaultPermissionViewSet(viewsets.ModelViewSet):
    queryset = DefaultPermission.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST', 'PATCH']:
            return DefaultPermissionSerializer2
        return DefaultPermissionSerializer1



class AttributeMapper(APIView):

    def post(self, request, *args, **kwargs):
        client = request.data['product_name']
        realm = request.data['organization_id']
        permissions = self.file_handle(request.data['permissions'])
        self.mapper(client, realm, permissions)
        return Response({"msg": "done"})


    @staticmethod
    def file_handle(permissions_file):
        file_name = os.path.join('', permissions_file.name)

        # Write the file to the desired location
        with open(file_name, 'wb+') as destination:
            for chunk in permissions_file.chunks():
                destination.write(chunk)
        
        with open(file_name, 'r') as f:
            data = json.load(f)
        os.remove(file_name)
        return data
    
    @staticmethod
    def mapper(client, realm, permissions):
        BASE_URL = 'http://localhost:8080/'

        master_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJOMEF2Zl9odmdoQzcxcUJ4cWs0blFKa2NnVkgxdjBXbnJWUDZ2QzhGREdVIn0.eyJleHAiOjE3MjAxNjA5MTcsImlhdCI6MTcyMDA3NDUxNywiYXV0aF90aW1lIjoxNzIwMDc0NTE3LCJqdGkiOiI0OTZlNjU3Yy01MDc0LTRkM2YtYWU5MC0yYjU2Nzk3ZjA3OTQiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvcmVhbG1zL21hc3RlciIsInN1YiI6IjFmMGMwMTJlLWRjYWMtNDA0YS1iMTFjLTUyN2E1ZGUwN2IxNSIsInR5cCI6IkJlYXJlciIsImF6cCI6InNlY3VyaXR5LWFkbWluLWNvbnNvbGUiLCJzaWQiOiI3MGI3MTY3MC1kN2VjLTQ2MzItOTc5OC0xMDk3YjU3ZDljYzAiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MCJdLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiJ9.iyMl7FO30B4rEL6vVm3teo60It6tsqRuKckjioMVc9D-kRkMOXWF9n-kTqzittDSpGEkRk8QVt3pbjbId_-Vxhvk8nw7M9MZGS-k62ZzQdEO96dU-fc6QCl_trXFP2WOE6JOhMSFMdyCia0TKpwAwALwdEcc93ypx2CFaAyhPm6tysN0u5tgreXh2dVMZVV3rqxZStb4y-TXLYsypohDB16g-gIMBOEmmRnfeqsxC_XiVWf3nSZiNqFspmhIOPVARj2_Yhp0jnDcv6ayXeJSwxoF2RceplUIa8xb0wjU0g6OSmDka6mWiaPAwwbPqf2PlZ-VfQhf3DhKVRZQh5O1NA'
        headers={"Authorization": 'Bearer %s' % master_token, "Content-Type": "application/json"}
        url = f'{BASE_URL}admin/realms/{realm}/clients'
        res = requests.get(url,headers=headers)
        data = res.json()
        for i in data:
            if client == i['clientId']:
                client = i['id']
                break

        url = f'{BASE_URL}admin/realms/{realm}/clients/{client}/protocol-mappers/models'
        
        payload = {
                "protocol": "openid-connect",
                "protocolMapper": "oidc-usermodel-attribute-mapper",
                "name": "newone",
                "config": {
                    "user.attribute": "EDA",
                    "claim.name": "permissions.EDA",
                    "jsonType.label": "String",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                    "multivalued": "true",
                    "aggregate.attrs": "true"
                }
            }
        for key, _ in permissions.items():
            payload["name"] = key
            payload["config"]["user.attribute"] = key
            payload["config"]["claim.name"] = f'permissions.{key}'

        
            res = requests.post(url, json.dumps(payload), headers=headers)
