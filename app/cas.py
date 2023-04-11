from fastapi import HTTPException, status, Request
import requests
import json

cas_url = "https://cas.apiit.edu.my"
cas_validate_url = f"{cas_url}/cas/p3/serviceValidate"


def cas_service_ticket_validator(request: Request, ticket: str = None):
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No service ticket provided")

    service_url = str(request.url).split("?")[0]

    validation_url = f"{cas_validate_url}?service={service_url}&ticket={ticket}&format=json"

    response = requests.get(validation_url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Service Ticket")

    service_response = response.json()['serviceResponse']
    if 'authenticationFailure' in service_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failure")

    attributes = service_response['authenticationSuccess']['attributes']
    distinguishedName = attributes['distinguishedName']
    parts = json.dumps(distinguishedName).lower()
    role = ""
    if ('ou=students' in parts):
        role = "student"
    if ('ou=academic' in parts):
        role = "academic"
    if ('ou=apiit tpm' in parts):
        role = "staff"

    # print(attributes)
    user = {
        "user_id": attributes['sAMAccountName'][0],
        "email": attributes['userPrincipalName'][0],
        "name": attributes['displayName'][0],
        "role": role
    }

    return user
