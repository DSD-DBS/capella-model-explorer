// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from "react";
import {Breadcrumbs} from "./Breadcrumbs";
import {ThemeSwitcher} from "./ThemeSwitcher";

export const Header = () => {
    return (
      <header className="header text-gray-700 p-4 flex justify-between items-center">
          <div><Breadcrumbs /></div>
          <div></div>
          <div><ThemeSwitcher /></div>
      </header>
    );
  };
