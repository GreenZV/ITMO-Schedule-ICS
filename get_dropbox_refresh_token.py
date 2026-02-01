from dropbox import DropboxOAuth2FlowNoRedirect

def get_dropbox_refresh_token(app_key, app_secret):
    auth_flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        app_secret,
        token_access_type='offline'
    )

    authorize_url = auth_flow.start()
    print(f"Перейдите по ссылке: {authorize_url}")
    print("Разрешите доступ и скопируйте код авторизации")

    auth_code = input("Введите код авторизации: ")

    oauth_result = auth_flow.finish(auth_code)

    print(f"Refresh Token: {oauth_result.refresh_token}")

def main():
    app_key = input("APP_KEY: ")
    app_secret = input("APP_SECRET: ")
    get_dropbox_refresh_token(app_key, app_secret)

if __name__ == "__main__":
    main()