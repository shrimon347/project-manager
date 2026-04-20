export interface WorkspaceResponse {
    id: string;
    name: string;
    description?: string;
    owner: User | string;
    color: string;
    members: {
        user: User;
        role: "admin" | "member" | "owner" | "viewer";
        joined_at: Date;
    }[];
    created_at: Date;
    updated_at: Date;
}
export interface WorkspaceApi {
    id: string;
    name: string;
    description?: string;
    color: string;
    created_at: string;
    member_count: number;
    role: string;
}
