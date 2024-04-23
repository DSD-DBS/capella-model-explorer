// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from "react";
import { Breadcrumbs } from "./Breadcrumbs";
import { ThemeSwitcher } from "./ThemeSwitcher";

export const Header = () => {
  return (
    <header className="flex items-center justify-between rounded-b-lg bg-gray-100 p-6 text-lg text-white shadow-lg dark:bg-custom-dark-2 dark:shadow-dark print:hidden">
      {" "}
      <div>
        <Breadcrumbs />
      </div>
      <div></div>
      <div>
        <ThemeSwitcher />
      </div>
    </header>
  );
};
