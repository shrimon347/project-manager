import { loggedOut, setAccessToken } from "@/store/slices/authSlice";
import type {
    AuthEnvelope,
    Login2faResponseData,
    LoginRequest,
    LoginResponseData,
    LogoutResponseData,
    MeUser,
    TokenRefreshResponseData,
} from "@/store/types/auth.types";
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

        login: builder.mutation<
            AuthEnvelope<LoginResponseData | Login2faResponseData>,
            LoginRequest
        >({
            query: (data) => ({
                url: "auth/login/",
                method: "POST",
                body: data,
            }),
            invalidatesTags: ["User"],
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled;
                    if ("access" in data.data) {
                        dispatch(setAccessToken(data.data.access));
                    }
                } catch {
                    // handled by caller
                }
            },
        }),

        getMe: builder.query<AuthEnvelope<MeUser>, void>({
            query: () => ({
                url: "auth/me/",
                method: "GET",
            }),
            providesTags: ["User"],
        }),

        refreshToken: builder.mutation<
            AuthEnvelope<TokenRefreshResponseData>,
            void
        >({
            query: () => ({
                url: "auth/refresh/",
                method: "POST",
                body: {},
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled;
                    dispatch(setAccessToken(data.data.access));
                } catch {
                    // handled by base query/auth guard
                }
            },
        }),
        logout: builder.mutation<AuthEnvelope<LogoutResponseData>, void>({
            query: () => ({
                url: "auth/logout/",
                method: "POST",
                body: {},
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    await queryFulfilled;
                    dispatch(loggedOut());
                } catch {
                    // Even if server logout fails, clear local auth state.
                    // This prevents stale access token from causing refresh attempts.
                    dispatch(loggedOut());
                }
            },
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
    useGetMeQuery,
    useRefreshTokenMutation,
    useLogoutMutation,
    useVerifyEmailMutation,
    useResendVerificationEmailMutation,
} = authApi;
