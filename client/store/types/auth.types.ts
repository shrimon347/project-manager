export type AuthEnvelope<T> = {
    success: boolean;
    message: string;
    data: T;
};

export type LoginRequest = {
    email: string;
    password: string;
};

export type LoginResponseData = {
    token_type: "Bearer";
    access_token: string;
};

export type Login2faResponseData = {
    requires_2fa: true;
    temp_token: string;
};

export type LogoutResponseData = Record<string, never>;

export type AuthState = {
    accessToken: string | null;
};
