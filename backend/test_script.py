from django.db import connections
try:
    with connections['sap_db'].cursor() as cursor:
        cursor.execute("SELECT DISTINCT T0.empID, (T0.firstName + ' ' + T0.lastName) as Name, T0.email FROM OHEM T0 INNER JOIN HEM6 T1 ON T0.empID = T1.empID WHERE T0.Active = 'Y' AND T1.roleID = 2")
        print(cursor.fetchall())
except Exception as e:
    print(e)
