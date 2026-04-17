import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import type { SerializedError } from "@reduxjs/toolkit";

/**
 * Matches backend `core.exceptions.custom_exception_handler` JSON body:
 * `{ success: false, message: string, code?: string, errors: ... }`
 *
 * `errors` uses the same nested dict / list / string leaves as Django's
 * `_normalize_errors` in `core/exceptions.py`.
 */
export type ApiErrorPayload = {
    success?: boolean;
    message?: string;
    code?: string;
    errors?: unknown;
};

function isPlainObject(value: unknown): value is Record<string, unknown> {
    return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Flattens normalized DRF-style error trees into a list of user-facing strings.
 */
export function collectApiErrorMessages(errors: unknown): string[] {
    if (errors === null || errors === undefined) {
        return [];
    }
    if (typeof errors === "string") {
        return errors.trim() ? [errors.trim()] : [];
    }
    if (typeof errors === "number" || typeof errors === "boolean") {
        return [String(errors)];
    }
    if (Array.isArray(errors)) {
        return errors.flatMap((item) => collectApiErrorMessages(item));
    }
    if (isPlainObject(errors)) {
        if (Object.keys(errors).length === 0) {
            return [];
        }
        return Object.values(errors).flatMap((item) =>
            collectApiErrorMessages(item),
        );
    }
    return [];
}

function messageFromFetchStyleData(data: Record<string, unknown>): string | null {
    if (typeof data.message === "string" && data.message.trim()) {
        return data.message.trim();
    }
    if (typeof data.detail === "string" && data.detail.trim()) {
        return data.detail.trim();
    }
    return null;
}

/**
 * Turns an RTK Query error (or thrown `unwrap()` error) into a single string
 * for inline alerts. When the API returns several field errors, they are joined.
 */
export function getApiErrorMessage(
    error: unknown,
    options?: { fallback?: string; separator?: string },
): string {
    const fallback =
        options?.fallback ?? "Something went wrong. Please try again.";
    const separator = options?.separator ?? " • ";

    if (error === null || error === undefined) {
        return fallback;
    }

    if (typeof error === "string" && error.trim()) {
        return error.trim();
    }

    if (typeof error === "object" && "message" in error) {
        const serialized = error as SerializedError;
        if (
            typeof serialized.message === "string" &&
            serialized.message.trim() &&
            !("status" in error)
        ) {
            return serialized.message.trim();
        }
    }

    if (typeof error !== "object" || !("status" in error)) {
        return fallback;
    }

    const fetchError = error as FetchBaseQueryError & {
        data?: unknown;
        error?: string;
    };

    if (
        fetchError.status === "FETCH_ERROR" ||
        fetchError.status === "TIMEOUT_ERROR" ||
        fetchError.status === "PARSING_ERROR"
    ) {
        const raw = fetchError.error?.trim();
        if (
            raw === "Failed to fetch" ||
            raw === "Load failed" ||
            fetchError.status === "TIMEOUT_ERROR"
        ) {
            return "Could not reach the API. Is the backend running, and is CORS allowing this app’s URL (e.g. http://localhost:3000)?";
        }
        return raw || fallback;
    }

    const { data } = fetchError;

    if (typeof data === "string" && data.trim()) {
        return data.trim();
    }

    if (!isPlainObject(data)) {
        return fallback;
    }

    const payload = data as ApiErrorPayload & Record<string, unknown>;

    const fieldMessages = collectApiErrorMessages(payload.errors);

    if (fieldMessages.length > 0) {
        return fieldMessages.join(separator);
    }

    const single = messageFromFetchStyleData(payload);
    if (single) {
        return single;
    }

    const loose = collectApiErrorMessages(
        Object.fromEntries(
            Object.entries(payload).filter(
                ([key]) =>
                    key !== "success" &&
                    key !== "code" &&
                    key !== "message" &&
                    key !== "errors",
            ),
        ),
    );
    if (loose.length > 0) {
        return loose.join(separator);
    }

    return fallback;
}
