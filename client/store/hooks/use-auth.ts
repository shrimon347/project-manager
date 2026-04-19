"use client";

import { useRouter } from "next/navigation";
import { useCallback, useMemo } from "react";
import { toast } from "sonner";

import { getApiErrorMessage } from "@/lib/api-error";
import { baseApi } from "@/store/api/baseApi";
import { useGetMeQuery, useLogoutMutation } from "@/store/api/authApi";
import { useAppDispatch, useAppSelector } from "@/store/hooks/redux-hooks";
import { loggedOut } from "@/store/slices/authSlice";

export function useAuth() {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const [logoutApi, { isLoading: isLoggingOut }] = useLogoutMutation();
    const {
        data: meEnvelope,
        isLoading: isUserLoading,
        isFetching: isUserFetching,
    } = useGetMeQuery(undefined, { skip: !accessToken });

    const user = useMemo(() => meEnvelope?.data ?? null, [meEnvelope]);

    const logout = useCallback(async () => {
        try {
            await logoutApi().unwrap();
            toast.success("Logged out successfully");
        } catch (error) {
            const message = getApiErrorMessage(error, {
                fallback: "Logout failed. Please try again.",
            });
            console.error(message);
            toast.error(message);
        } finally {
            dispatch(loggedOut());
            dispatch(baseApi.util.resetApiState());
            router.replace("/login");
        }
    }, [dispatch, logoutApi, router]);

    return {
        isAuthenticated: Boolean(accessToken),
        accessToken,
        user,
        isUserLoading,
        isUserFetching,
        logout,
        isLoggingOut,
    };
}
