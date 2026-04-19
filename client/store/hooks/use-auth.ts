"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { toast } from "sonner";

import { getApiErrorMessage } from "@/lib/api-error";
import { useLogoutMutation } from "@/store/api/authApi";
import { useAppDispatch, useAppSelector } from "@/store/hooks/redux-hooks";
import { loggedOut } from "@/store/slices/authSlice";

export function useAuth() {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const [logoutApi, { isLoading: isLoggingOut }] = useLogoutMutation();

    const logout = useCallback(async () => {
        try {
            await logoutApi().unwrap();

            // SUCCESS TOAST
            toast.success("Logged out successfully");
        } catch (error) {
            const message = getApiErrorMessage(error, {
                fallback: "Logout failed. Please try again.",
            });

            console.error(message);

            // ERROR TOAST
            toast.error(message);
        } finally {
            // always clear session
            dispatch(loggedOut());

            // redirect
            router.replace("/login");
        }
    }, [dispatch, logoutApi, router]);

    return {
        isAuthenticated: Boolean(accessToken),
        accessToken,
        logout,
        isLoggingOut,
    };
}
