#!/usr/bin/env python3
"""
Basic authentication module
"""
from .auth import Auth
from typing import TypeVar
from models.user import User


class BasicAuth(Auth):
    """ class that implements Basic Authentication """
    def extract_base64_authorization_header(
            self, authorization_header: str
    ) -> str:
        """
        method that returns the base64 part of the `Authorization` header
        for basic authentication
        """
        if authorization_header:
            if isinstance(authorization_header, str):
                if authorization_header.startswith('Basic '):
                    return authorization_header.split()[1]
        return None

    def decode_base64_authorization_header(
            self, base64_authorization_header: str
    ) -> str:
        """
        method that returns the decoded value of a Base64 string stored
        in `base64_authorization_header` argument
        """
        from base64 import b64decode, binascii

        if base64_authorization_header:
            if isinstance(base64_authorization_header, str):
                try:
                    bin_val = b64decode(base64_authorization_header)
                except binascii.Error:
                    return None
                else:
                    str_val = bin_val.decode(encoding='utf-8')
                    return str_val
        return None

    def extract_user_credentials(
            self, decoded_base64_authorization_header: str
    ) -> (str, str):
        """
        method that returns the user email and password from the Base64
        decoded value
        """
        if decoded_base64_authorization_header:
            if isinstance(decoded_base64_authorization_header, str):
                if ":" in decoded_base64_authorization_header:
                    idx = decoded_base64_authorization_header.find(':')
                    u_email = decoded_base64_authorization_header[:idx]
                    u_passwd = decoded_base64_authorization_header[idx + 1:]
                    return u_email, u_passwd
        return None, None

    def user_object_from_credentials(
            self, user_email: str, user_pwd: str
    ) -> TypeVar('User'):
        """
        method that returns the User instance based on user `email` and
        `password`
        """
        if user_email and type(user_email) is str \
           and user_pwd and type(user_pwd) is str:
            try:
                user_list = User.search(attributes={'email': user_email})
            except Exception:
                user_list = None

            if user_list:
                user = user_list[0]
                if user.is_valid_password(user_pwd):
                    return user
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """
        method that overloads `Auth` and retrieves `User` instance for
        a request
        """
        if request:
            auth_head_val = super().authorization_header(request)
            if auth_head_val:
                b64credential = self.extract_base64_authorization_header(
                    auth_head_val)
                if b64credential:
                    str_credential = self.decode_base64_authorization_header(
                        b64credential)
                    if str_credential:
                        u_email, u_passwd = self.extract_user_credentials(
                            str_credential)
                        if u_email and u_passwd:
                            return self.user_object_from_credentials(
                                u_email, u_passwd)
        return None
