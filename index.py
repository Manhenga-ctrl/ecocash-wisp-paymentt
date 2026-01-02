from routeros_api import RouterOsApiPool

api_pool = RouterOsApiPool(
    '52.22.85.41:14349',
    username='chiponda',
    password='admin',
    plaintext_login=True
)

api = api_pool.get_api()
hotspot_users = api.get_resource('/ip/hotspot/user')

vouchers = hotspot_users.get()

for v in vouchers:
    print(v['name'], v.get('profile'))

api_pool.disconnect()
