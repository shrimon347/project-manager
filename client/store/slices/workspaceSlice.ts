import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { Workspace } from "../types/workspace.types";

interface WorkspaceState {
    currentWorkspace: Workspace | null;
}
const initialState: WorkspaceState = {
    currentWorkspace: null,
};

const workspaceSlice = createSlice({
    name: "workspace",
    initialState,
    reducers: {
        setWorkspace(state, action: PayloadAction<Workspace>) {
            state.currentWorkspace = action.payload;
        },
    },
});

export const { setWorkspace } = workspaceSlice.actions;
export default workspaceSlice.reducer;
