"use client";

import { getApiErrorMessage } from "@/lib/api-error";
import { registerSchema } from "@/lib/validations/auth.schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { z } from "zod";

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
import { useRegisterMutation } from "@/store/api/authApi";
import Link from "next/link";

import { CheckCircle, Eye, EyeOff } from "lucide-react";
import { toast } from "sonner";

type FormData = z.infer<typeof registerSchema>;

export function SignupForm({
    className,
    ...props
}: React.ComponentProps<"form">) {
    const router = useRouter();
    const [registerUser, { isLoading }] = useRegisterMutation();
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isPasswordFocused, setIsPasswordFocused] = useState(false);

    const {
        register,
        handleSubmit,
        control,
        reset,
        formState: { errors },
    } = useForm<FormData>({
        resolver: zodResolver(registerSchema),
        mode: "onChange",
    });

    const password = useWatch({ control, name: "password" }) || "";
    // password checks
    const checks = {
        length: password.length >= 8,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        symbol: /[^A-Za-z0-9]/.test(password),
    };

    const showRules = isPasswordFocused && password.length > 0;
    const onSubmit = async (data: FormData) => {
        setSubmitError(null);

        try {
            const payload = {
                name: data.name,
                email: data.email,
                password: data.password,
                confirm_password: data.confirm_password,
            };

            await registerUser(payload).unwrap();
            reset();
            toast.success("Account created successfully.", {
                description:
                    "Check your email for a verification link. You can request a new one from the login page if needed.",
                icon: <CheckCircle className="text-green-500" />,
            });
            router.push("/login");
        } catch (error) {
            setSubmitError(
                getApiErrorMessage(error, {
                    fallback: "Signup failed. Please try again.",
                    separator: "\n",
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
                {/* HEADER */}
                <div className="flex flex-col items-center gap-1 text-center">
                    <h1 className="text-2xl font-bold">Create your account</h1>
                    <p className="text-sm text-muted-foreground">
                        Fill in the form below to create your account
                    </p>
                </div>

                {/* NAME */}
                <Field>
                    <FieldLabel>Full Name</FieldLabel>
                    <Input {...register("name")} placeholder="John Doe" />
                    {errors.name && (
                        <p className="text-red-500 text-sm">
                            {errors.name.message}
                        </p>
                    )}
                </Field>

                {/* EMAIL */}
                <Field>
                    <FieldLabel>Email</FieldLabel>
                    <Input {...register("email")} placeholder="m@example.com" />
                    <FieldDescription>
                        We’ll use this to contact you.
                    </FieldDescription>
                    {errors.email && (
                        <p className="text-red-500 text-sm">
                            {errors.email.message}
                        </p>
                    )}
                </Field>

                {/* PASSWORD */}
                <Field>
                    <FieldLabel>Password</FieldLabel>

                    <div className="relative">
                        <Input
                            type={showPassword ? "text" : "password"}
                            {...register("password")}
                            className={cn(
                                "pr-10",
                                errors.password && "border-destructive",
                            )}
                            onFocus={() => setIsPasswordFocused(true)}
                            onBlur={() => setIsPasswordFocused(false)}
                        />

                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-1/2 -translate-y-1/2"
                        >
                            {showPassword ? (
                                <Eye size={14} className="text-primary" />
                            ) : (
                                <EyeOff size={14} className="text-primary" />
                            )}
                        </button>
                    </div>

                    {showRules && (
                        <div className="mt-2 space-y-1 text-sm">
                            <div className="flex items-center gap-2">
                                <span
                                    className={
                                        checks.length
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {checks.length ? "✔" : "•"}
                                </span>
                                <span
                                    className={
                                        checks.length
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    8+ characters
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                <span
                                    className={
                                        checks.upper
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {checks.upper ? "✔" : "•"}
                                </span>
                                <span
                                    className={
                                        checks.upper
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    Uppercase letter
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                <span
                                    className={
                                        checks.lower
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {checks.lower ? "✔" : "•"}
                                </span>
                                <span
                                    className={
                                        checks.lower
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    Lowercase letter
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                <span
                                    className={
                                        checks.number
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {checks.number ? "✔" : "•"}
                                </span>
                                <span
                                    className={
                                        checks.number
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    Number
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                <span
                                    className={
                                        checks.symbol
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {checks.symbol ? "✔" : "•"}
                                </span>
                                <span
                                    className={
                                        checks.symbol
                                            ? "text-green-500"
                                            : "text-muted-foreground"
                                    }
                                >
                                    Symbol
                                </span>
                            </div>
                        </div>
                    )}

                    {errors.password && (
                        <p className="text-destructive text-sm mt-1">
                            {errors.password.message}
                        </p>
                    )}
                </Field>

                {/* CONFIRM PASSWORD */}
                <Field>
                    <FieldLabel>Confirm Password</FieldLabel>

                    <div className="relative">
                        <Input
                            type={showConfirmPassword ? "text" : "password"}
                            {...register("confirm_password")}
                            className={cn(
                                "pr-10",
                                errors.confirm_password && "border-destructive",
                            )}
                        />

                        <button
                            type="button"
                            onClick={() =>
                                setShowConfirmPassword(!showConfirmPassword)
                            }
                            className="absolute right-3 top-1/2 -translate-y-1/2"
                        >
                            {showConfirmPassword ? (
                                <Eye size={14} className="text-primary" />
                            ) : (
                                <EyeOff size={14} className="text-primary" />
                            )}
                        </button>
                    </div>

                    {errors.confirm_password && (
                        <p className="text-destructive text-sm">
                            {errors.confirm_password.message}
                        </p>
                    )}
                </Field>

                {/* SUBMIT */}
                <Field>
                    <Button
                        type="submit"
                        className="w-full"
                        disabled={isLoading}
                    >
                        {isLoading && (
                            <Spinner className="shrink-0" aria-hidden />
                        )}
                        {isLoading ? "Creating account..." : "Create Account"}
                    </Button>
                    {submitError && (
                        <p className="text-destructive text-sm mt-2 whitespace-pre-line">
                            {submitError}
                        </p>
                    )}
                </Field>

                {/* SOCIAL */}
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

                    <FieldDescription className="px-6 text-center">
                        Already have an account?{" "}
                        <Link href="/login">Sign in</Link>
                    </FieldDescription>
                </Field>
            </FieldGroup>
        </form>
    );
}
