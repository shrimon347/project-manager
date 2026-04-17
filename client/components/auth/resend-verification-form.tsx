"use client";

import { Button } from "@/components/ui/button";
import {
    Field,
    FieldDescription,
    FieldGroup,
    FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { getApiErrorMessage } from "@/lib/api-error";
import { cn } from "@/lib/utils";
import { useResendVerificationEmailMutation } from "@/store/api/authApi";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

export function ResendVerificationForm({
    className,
    ...props
}: React.ComponentProps<"form">) {
    const [email, setEmail] = useState("");
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [resend, { isLoading }] = useResendVerificationEmailMutation();

    const onSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitError(null);
        try {
            const result = await resend({ email: email.trim().toLowerCase() }).unwrap();
            toast.success(result.message);
        } catch (err) {
            setSubmitError(
                getApiErrorMessage(err, {
                    fallback: "Could not send email. Please try again.",
                    separator: "\n",
                }),
            );
        }
    };

    return (
        <form
            onSubmit={onSubmit}
            className={cn("flex flex-col gap-6", className)}
            {...props}
        >
            <FieldGroup>
                <div className="flex flex-col items-center gap-1 text-center">
                    <h1 className="text-2xl font-bold">Resend verification email</h1>
                    <p className="text-sm text-balance text-muted-foreground">
                        Enter the email you signed up with. We will send a new
                        link if the account exists and is not verified yet.
                    </p>
                </div>
                <Field>
                    <FieldLabel htmlFor="resend-email">Email</FieldLabel>
                    <Input
                        id="resend-email"
                        type="email"
                        autoComplete="email"
                        placeholder="m@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </Field>
                <Field>
                    <Button type="submit" className="w-full" disabled={isLoading}>
                        {isLoading && (
                            <Spinner className="shrink-0" aria-hidden />
                        )}
                        {isLoading ? "Sending…" : "Send verification email"}
                    </Button>
                    {submitError && (
                        <p className="text-destructive text-sm mt-2 whitespace-pre-line">
                            {submitError}
                        </p>
                    )}
                    <FieldDescription className="text-center">
                        <Link
                            href="/login"
                            className="underline underline-offset-4"
                        >
                            Back to login
                        </Link>
                    </FieldDescription>
                </Field>
            </FieldGroup>
        </form>
    );
}
