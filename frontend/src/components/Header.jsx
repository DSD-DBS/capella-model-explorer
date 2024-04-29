// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from "react";
import { Breadcrumbs } from "./Breadcrumbs";
import { ThemeSwitcher } from "./ThemeSwitcher";
import { SettingsMenu } from "./SettingsMenu";

export const Header = () => {
  return (
    <header className="fixed left-0 top-0 z-50 w-screen items-center justify-between rounded-b-lg bg-gray-100 p-6 text-lg text-white shadow-lg dark:bg-custom-dark-2 dark:shadow-dark print:hidden">
      <div className="flex items-center justify-between">
        <Breadcrumbs />
        <div className="flex flex-shrink-0 space-x-4">
          <SettingsMenu />
          <ThemeSwitcher />
        </div>
      </div>
    </header>
  );
};
