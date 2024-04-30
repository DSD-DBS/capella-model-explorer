import React, { useState, useEffect, useRef } from "react";
import { ListCollapseIcon } from "lucide-react";

export const SidebarIcon = () => {
  return (
    <div className="flex cursor-pointer items-center justify-center rounded-full bg-custom-light p-2 transition-colors duration-300 ease-in-out hover:bg-custom-dark-4 dark:bg-custom-dark-1 dark:hover:bg-custom-light">
      <ListCollapseIcon />
    </div>
  );
};
