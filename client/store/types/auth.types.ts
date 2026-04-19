export type AuthEnvelope<T> = {
    success: boolean;
    message: string;
    data: T;
};

export type LoginRequest = {
    email: string;
    password: string;
};

/** Current user from `GET /auth/me/` (and optional echo on login; app should use `/me` only). */
export type MeUser = {
    id: string;
    email: string;
    name: string | null;
};

export type LoginResponseData = {
    access: string;
    user: MeUser;
};

export type TokenRefreshResponseData = {
    access: string;
};

export type Login2faResponseData = {
    requires_2fa: true;
    temp_token: string;
};

export type LogoutResponseData = Record<string, never>;

export type AuthState = {
    accessToken: string | null;
};
