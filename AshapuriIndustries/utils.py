from rest_framework_simplejwt.tokens import RefreshToken


def generate_jwt_token(user):
    #jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    #jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    #
    #    payload = jwt_payload_handler(user)
    #    return jwt_encode_handler(payload)

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
