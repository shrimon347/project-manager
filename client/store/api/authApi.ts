import { baseApi } from "./baseApi";
import { setAccessToken } from "@/store/slices/authSlice";
import type {
    AuthEnvelope,
    Login2faResponseData,
    LoginRequest,
    LoginResponseData,
    LogoutResponseData,
} from "@/store/types/auth.types";

export const authApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        register: builder.mutation({
            query: (data) => ({
                url: "auth/register/",
                method: "POST",
                body: data,
            }),
        }),

        login: builder.mutation<
            AuthEnvelope<LoginResponseData | Login2faResponseData>,
            LoginRequest
        >({
            query: (data) => ({
                url: "auth/login/",
                method: "POST",
                body: data,
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled;
                    if ("access_token" in data.data) {
                        dispatch(setAccessToken(data.data.access_token));
                    }
                } catch {
                    // handled by caller
                }
            },
        }),

        refreshToken: builder.mutation<AuthEnvelope<LoginResponseData>, void>({
            query: () => ({
                url: "auth/refresh/",
                method: "POST",
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled;
                    dispatch(setAccessToken(data.data.access_token));
                } catch {
                    // handled by base query/auth guard
                }
            },
        }),
        logout: builder.mutation<AuthEnvelope<LogoutResponseData>, void>({
            query: () => ({
                url: "auth/logout/",
                method: "POST",
            }),
        }),

        verifyEmail: builder.mutation<
            { success: boolean; message: string; data: unknown },
            { email: string; token: string }
        >({
            query: (body) => ({
                url: "auth/verify-email/",
                method: "POST",
                body,
            }),
        }),

        resendVerificationEmail: builder.mutation<
            { success: boolean; message: string; data: unknown },
            { email: string }
        >({
            query: (body) => ({
                url: "auth/resend-verification-email/",
                method: "POST",
                body,
            }),
        }),
    }),
});

export const {
    useRegisterMutation,
    useLoginMutation,
    useRefreshTokenMutation,
    useLogoutMutation,
    useVerifyEmailMutation,
    useResendVerificationEmailMutation,
} = authApi;
