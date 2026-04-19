"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { useGetMeQuery } from "@/store/api/authApi";
import { baseApi } from "@/store/api/baseApi";
import { useAppDispatch, useAppSelector } from "@/store/hooks/redux-hooks";
import { loggedOut } from "@/store/slices/authSlice";

type AuthSessionProviderProps = {
    children: ReactNode;
};

/**
 * Subscribes to `/auth/me` whenever an access token exists so the user is cached globally.
 * If the session is rejected with 401, clears auth and sends the user to login.
 */
export function AuthSessionProvider({ children }: AuthSessionProviderProps) {
    const dispatch = useAppDispatch();
    const router = useRouter();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const { error } = useGetMeQuery(undefined, { skip: !accessToken });

    useEffect(() => {
        if (!accessToken || !error) {
            return;
        }
        const status = "status" in error ? error.status : undefined;
        if (status === 401) {
            dispatch(loggedOut());
            dispatch(baseApi.util.resetApiState());
            router.replace("/login");
        }
    }, [accessToken, dispatch, error, router]);

    return children;
}
