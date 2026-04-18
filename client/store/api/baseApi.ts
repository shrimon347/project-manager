import {
    BaseQueryFn,
    FetchArgs,
    FetchBaseQueryError,
    createApi,
    fetchBaseQuery,
} from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/store";
import { loggedOut, setAccessToken } from "@/store/slices/authSlice";

import { API_BASE_URL } from "@/lib/api-base-url";

const rawBaseQuery = fetchBaseQuery({
    baseUrl: API_BASE_URL,
    credentials: "include",
    prepareHeaders: (headers, { getState }) => {
        const token = (getState() as RootState).auth.accessToken;
        if (token) {
            headers.set("authorization", `Bearer ${token}`);
        }
        return headers;
    },
});

const baseQueryWithReauth: BaseQueryFn<
    string | FetchArgs,
    unknown,
    FetchBaseQueryError
> = async (args, api, extraOptions) => {
    let result = await rawBaseQuery(args, api, extraOptions);

    if (result.error?.status === 401) {
        const refreshResult = await rawBaseQuery(
            {
                url: "auth/refresh/",
                method: "POST",
            },
            api,
            extraOptions,
        );

        if (refreshResult.data) {
            const data = refreshResult.data as {
                data?: { access_token?: string };
            };
            const newAccessToken = data.data?.access_token;

            if (newAccessToken) {
                api.dispatch(setAccessToken(newAccessToken));
                result = await rawBaseQuery(args, api, extraOptions);
            } else {
                api.dispatch(loggedOut());
            }
        } else {
            api.dispatch(loggedOut());
        }
    }

    return result;
};

export const baseApi = createApi({
    reducerPath: "api",

    baseQuery: baseQueryWithReauth,

    endpoints: () => ({}), // empty, we inject later
});
