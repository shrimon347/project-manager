import { WorkspaceApi } from "../types/workspace.types";
import { baseApi } from "./baseApi";

export const workspaceApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getWorkspaces: builder.query<WorkspaceApi[], void>({
            query: () => ({
                url: "workspaces/",
                method: "GET",
            }),
            transformResponse: (response: WorkspaceApi) => {
                return response.data.workspaces.map((ws: WorkspaceApi) => ({
                  ...ws,
                  created_at: new Date(ws.created_at),
                }));
              },
            providesTags: ["Workspace"],
        }),
    }),
});

export const { useGetWorkspacesQuery } = workspaceApi;
