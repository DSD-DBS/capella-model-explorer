// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from "react";
import { Home } from "lucide-react";
import { Link } from "react-router-dom";

export const HomeIcon = () => {
  return (
    <Link to="/">
      <div className="flex cursor-pointer items-center justify-center rounded-full bg-custom-light p-2 transition-colors duration-300 ease-in-out hover:bg-custom-dark-4 dark:bg-custom-dark-1 dark:hover:bg-custom-light">
        <Home className="h-6 w-6 text-black dark:text-white" />
      </div>
    </Link>
  );
};
