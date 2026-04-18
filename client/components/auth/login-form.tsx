"use client";

import { Button } from "@/components/ui/button";
import {
    Field,
    FieldDescription,
    FieldGroup,
    FieldLabel,
    FieldSeparator,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";
import { getApiErrorMessage } from "@/lib/api-error";
import { loginSchema } from "@/store/schemas/auth.schema";
import { useLoginMutation } from "@/store/api/authApi";
import { useAppSelector } from "@/store/hooks/redux-hooks";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm({
    className,
    ...props
}: React.ComponentProps<"form">) {
    const router = useRouter();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const [login, { isLoading }] = useLoginMutation();
    const [showPassword, setShowPassword] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    });

    useEffect(() => {
        if (accessToken) {
            router.replace("/dashboard");
        }
    }, [accessToken, router]);

    const onSubmit = async (data: LoginFormData) => {
        setSubmitError(null);

        try {
            const response = await login({
                email: data.email.trim().toLowerCase(),
                password: data.password,
            }).unwrap();

            if ("access_token" in response.data) {
                router.replace("/dashboard");
                return;
            }

            setSubmitError(
                "Two-factor authentication is required for this account, but the 2FA login screen is not implemented yet.",
            );
        } catch (error) {
            setSubmitError(
                getApiErrorMessage(error, {
                    fallback: "Login failed. Please try again.",
                }),
            );
        }
    };

    return (
        <form
            onSubmit={handleSubmit(onSubmit)}
            className={cn("flex flex-col gap-6", className)}
            {...props}
        >
            <FieldGroup>
                <div className="flex flex-col items-center gap-1 text-center">
                    <h1 className="text-2xl font-bold">
                        Login to your account
                    </h1>
                    <p className="text-sm text-balance text-muted-foreground">
                        Enter your email below to login to your account
                    </p>
                </div>
                <Field>
                    <FieldLabel htmlFor="email">Email</FieldLabel>
                    <Input
                        id="email"
                        type="email"
                        placeholder="m@example.com"
                        {...register("email")}
                        required
                    />
                    {errors.email ? (
                        <p className="text-sm text-destructive">
                            {errors.email.message}
                        </p>
                    ) : null}
                </Field>
                <Field>
                    <div className="flex items-center">
                        <FieldLabel htmlFor="password">Password</FieldLabel>
                        <a
                            href="#"
                            className="ml-auto text-sm underline-offset-4 hover:underline"
                        >
                            Forgot your password?
                        </a>
                    </div>
                    <div className="relative">
                        <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            className="pr-10"
                            {...register("password")}
                            required
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword((previous) => !previous)}
                            className="absolute right-3 top-1/2 -translate-y-1/2"
                            aria-label={
                                showPassword ? "Hide password" : "Show password"
                            }
                        >
                            {showPassword ? (
                                <Eye size={14} className="text-primary" />
                            ) : (
                                <EyeOff size={14} className="text-primary" />
                            )}
                        </button>
                    </div>
                    {errors.password ? (
                        <p className="text-sm text-destructive">
                            {errors.password.message}
                        </p>
                    ) : null}
                </Field>
                <Field>
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <Spinner className="shrink-0" aria-hidden />
                                Signing in...
                            </>
                        ) : (
                            "Login"
                        )}
                    </Button>
                    {submitError ? (
                        <p className="mt-2 whitespace-pre-line text-sm text-destructive">
                            {submitError}
                        </p>
                    ) : null}
                </Field>
                <FieldSeparator>Or continue with</FieldSeparator>
                <Field>
                    <Button variant="outline" type="button">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                        >
                            <path
                                d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
                                fill="currentColor"
                            />
                        </svg>
                        Login with GitHub
                    </Button>
                    <FieldDescription className="text-center">
                        Don&apos;t have an account?{" "}
                        <Link
                            href="/signup"
                            className="underline underline-offset-4"
                        >
                            Sign up
                        </Link>
                        <span className="mx-1 text-muted-foreground">·</span>
                        <Link
                            href="/resend-verification"
                            className="underline"
                        >
                            Resend verification
                        </Link>
                    </FieldDescription>
                </Field>
            </FieldGroup>
        </form>
    );
}
