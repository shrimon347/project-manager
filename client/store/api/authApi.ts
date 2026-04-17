import { baseApi } from "./baseApi";

export const authApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        register: builder.mutation({
            query: (data) => ({
                url: "auth/register/",
                method: "POST",
                body: data,
            }),
        }),

        login: builder.mutation({
            query: (data) => ({
                url: "auth/login/",
                method: "POST",
                body: data,
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
    useVerifyEmailMutation,
    useResendVerificationEmailMutation,
} = authApi;
