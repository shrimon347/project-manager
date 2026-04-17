"use client";

import { getApiErrorMessage } from "@/lib/api-error";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { useVerifyEmailMutation } from "@/store/api/authApi";

import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { AlertCircle, CheckCheck, Loader2 } from "lucide-react";

type Status = "loading" | "success" | "error";

type StatusConfig = {
    badge: string;
    badgeVariant: "secondary" | "destructive" | "outline";
    title: string;
    description: string;
    iconColor: string;
    iconBg: string;
};

const statusConfig: Record<Status, StatusConfig> = {
    loading: {
        badge: "Verifying",
        badgeVariant: "secondary",
        title: "Checking your link…",
        description: "This only takes a moment.",
        iconColor: "text-muted-foreground",
        iconBg: "bg-muted",
    },
    error: {
        badge: "Failed",
        badgeVariant: "destructive",
        title: "Verification failed",
        description: "This link may be expired or already used.",
        iconColor: "text-destructive",
        iconBg: "bg-destructive/10",
    },
    success: {
        badge: "Verified",
        badgeVariant: "outline",
        title: "You're all set",
        description: "Redirecting you to login in a moment…",
        iconColor: "text-green-600",
        iconBg: "bg-green-50 dark:bg-green-950/30",
    },
};

export function VerifyEmailHandler() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [verifyEmail] = useVerifyEmailMutation();

    const email = searchParams.get("email")?.trim() ?? "";
    const token = searchParams.get("token")?.trim() ?? "";

    const [status, setStatus] = useState<Status>(() =>
        !email || !token ? "error" : "loading",
    );

    const [errorMessage, setErrorMessage] = useState<string | null>(() =>
        !email || !token ? "This link is missing an email or token." : null,
    );

    const ran = useRef(false);

    useEffect(() => {
        if (!email || !token) return;
        if (ran.current) return;
        ran.current = true;

        verifyEmail({ email, token })
            .unwrap()
            .then((payload) => {
                setStatus("success");
                toast.success(
                    payload.message ?? "Email verified successfully.",
                );
                setTimeout(() => router.push("/login"), 10000);
            })
            .catch((err) => {
                setStatus("error");
                setErrorMessage(
                    getApiErrorMessage(err, {
                        fallback: "Could not verify email. Please try again.",
                        separator: "\n",
                    }),
                );
            });
    }, [email, token, router, verifyEmail]);

    const config = statusConfig[status];

    return (
        <div className="mx-auto flex w-full max-w-md min-h-[50vh] flex-col justify-center sm:min-h-[60vh]">
            <Card className="w-full shadow-sm animate-in fade-in zoom-in-95 duration-300">
                <CardHeader className="space-y-1.5 pb-0">
                    <CardTitle className="text-lg font-medium">
                        Email verification
                    </CardTitle>
                    <CardDescription>
                        {status === "error" && errorMessage
                            ? "We weren't able to verify your address."
                            : config.description}
                    </CardDescription>
                </CardHeader>

                <div className="mx-4 mt-4 h-px bg-border" />

                <CardContent className="flex w-full flex-col items-center gap-3 pt-2 pb-6 text-center">
                    {/* Icon */}
                    <div
                        className={cn(
                            "flex size-14 shrink-0 items-center justify-center rounded-full",
                            config.iconBg,
                        )}
                    >
                        {status === "loading" && (
                            <Loader2
                                className={cn(
                                    "h-6 w-6 animate-spin",
                                    config.iconColor,
                                )}
                            />
                        )}
                        {status === "error" && (
                            <AlertCircle
                                className={cn("h-6 w-6", config.iconColor)}
                            />
                        )}
                        {status === "success" && (
                            <CheckCheck
                                className={cn("h-6 w-6", config.iconColor)}
                            />
                        )}
                    </div>

                    {/* Badge */}
                    <Badge variant={config.badgeVariant} className="text-xs">
                        {config.badge}
                    </Badge>

                    {/* Text */}
                    <p className="text-sm font-medium text-foreground">
                        {config.title}
                    </p>

                    {status === "error" && errorMessage && (
                        <p className="w-full max-w-full text-balance text-xs text-destructive whitespace-pre-line">
                            {errorMessage}
                        </p>
                    )}

                    {/* Progress bar */}
                    {(status === "loading" || status === "success") && (
                        <div className="w-full h-0.5 rounded-full bg-muted overflow-hidden mt-1">
                            <div
                                className={cn(
                                    "h-full rounded-full transition-all",
                                    status === "loading"
                                        ? "w-2/5 animate-[shimmer_1.2s_ease-in-out_infinite]"
                                        : "w-full bg-green-500",
                                )}
                            />
                        </div>
                    )}

                    {/* Error actions */}
                    {status === "error" && (
                        <div className="flex flex-col items-center gap-1.5 mt-1">
                            <Link
                                href="/resend-verification"
                                className="text-xs font-medium text-primary hover:underline"
                            >
                                Resend verification email
                            </Link>
                            <Link
                                href="/login"
                                className="text-xs text-muted-foreground hover:underline"
                            >
                                Back to login
                            </Link>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
