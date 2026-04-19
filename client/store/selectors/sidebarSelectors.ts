import { RootState } from "@/store";

export const selectSidebarOpenState = (state: RootState) => {
    const s = state.sidebar;

    return s.isOpen || (s.settings.isHoverOpen && s.isHover);
};
