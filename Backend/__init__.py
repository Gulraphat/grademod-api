import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "modgrade-6986f",
  "private_key_id": "ce2081bc2b15b34d8a7f00257daaca185d644844",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz0DBVdKRkyu6H\nI8ZZbWLccFM7NvV0IFqg7r8ORorrvf+C1lO+u36TC/Vj0PE2+KHBhYsHGPkoZkKJ\nBgUDgQ1HqL581Pk4yA3pQ76tP1WQ/5noQp5FcBtIsk/goq047mgwA6KAUZ2LCXHX\n1KVd+I8bptbvWtwmGoU5nMhzbotzxihj+c+p2/3crCk/Lgv76LY1pNKVD6p45V+v\nFhq8a877DU0Tm46KqZVSfqnS5RymMzQB+Cw0qrCpyfYuCAoi2o4FERHPbKiKe+5B\n+n55XvUI3aVbT8ocngXlpkh1IJ1r0MGZVOczCC9m0gNeBtcQ7RYqV+kDPgWKvXLO\nGtARTNhtAgMBAAECggEAHDgz4bFy3FupyB0x85ZycbiSI2SqbF1og8G8S8P/6OPy\nXej/jxszT+YMTqw7sv4duraX3VcKwU+dKQ6ACm7+M80UihhNfZ8N6donKl7aca1f\njN8poimoKoZLeWxmZZ0qzkA/yEYmxKuIiZAWnNMVuIf8Sue2TaeTWXmUzuLeMV63\n18MwnkQf8VgmdhmRv7noz9xnoTP+PxjDsqI5HX2/wj7kkP8NR7QSAdzGIjYvJBia\nIwRy3Mmjh5spsMB2/i8DQAxh7tgztU3nArQ4IJPtokbh4gE6us3+LovYXhJj2KGi\nmB0nbL68uNUXEGAcPT4onRuQw//mtwnD63vXuY3nUQKBgQDzOnSijnzibC5whW08\nQgJ1olu7nZeVbqid+ZkyFhJSQP5Kz4iPrKuecY57lxInzAtQEEaGo4ayxyLZh086\nhNF5nfx9vN1Q0GTecyKGLJktfmpTIVsKmQ9J2Lm+GYbTKEC0/pyy7DpmkXxv5Vdx\nD90r66Pc2tzRTglbwj8FGAKJPQKBgQC9QUoT7PB6c5sz0bPsEyN8qMj7Jj8tvCBA\nEmRRRp6mfHO7IHW6NTqifzm33p2QmC3FZq5bqAoUXg17vuR5dPRRHTWx7btXN21d\nwsdY++W23AInn6wpuZaWdAFbXH8g8vaMApkaaYJJpl2DKClgFX/ZVoZaQs8J0Eh3\ndsq+hm6e8QKBgQCx72m0Ihkqa4ntty6ajo/ODuCc+EUUhMfGCfsQsSTmF7XwdLKq\nqN9EIj7iGzqk8pi0EbQGe0rnLtdH270SSmgUWIeGVMxzeoDQW9o93hKRPZH7DsPT\nlPWiSHJZp8MCZsgvoLRyEG8I6hXmphi6FajvoItX3qT8WeJuxkPkLhRs4QKBgDEI\nADwnT6o510TWmImZ78C1LdS7dPTRX32aBjl0VVgGuCkL4NRMRBOjaH21hBbZBkq1\nLoj6gRoDv/SGYUUCQuXc7nNZhwayingXJXRtVndIippfaMgql9QE2/EihqEvsSZW\n6fmIykNwgZugRQ/qogPZwdcSpfcB6jRhJ2ezBmfRAoGAN4pPce2O48wuggI7dVbJ\n8zxFRqJPXb1oM67SftmUOynOKvp0oXt0qDbe9CtDlahuTT87uDPL/ydmaP5L9jOg\nNr6d0P3NinR8uDei88AO+cJz5GiirSn+jpRWsWky5iw22NtnZuE6Cfd/TaMDkLZm\n7K6dGMSQFQfwzSEuOmSO4SA=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-waxr7@modgrade-6986f.iam.gserviceaccount.com",
  "client_id": "104657316716170448238",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-waxr7%40modgrade-6986f.iam.gserviceaccount.com"
})

# เรียกใช้ initialize_app() เพื่อสร้าง default app ของ Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://modgrade-6986f-default-rtdb.asia-southeast1.firebasedatabase.app/'
})