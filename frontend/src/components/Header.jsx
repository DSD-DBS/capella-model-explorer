import React from "react";
import {Breadcrumbs} from "./Breadcrumbs";
import {ThemeSwitcher} from "./ThemeSwitcher";

export const Header = () => {
    return (
      <header className=" text-gray-700 p-4 flex justify-between items-center">
          <div><Breadcrumbs /></div>
          <div></div>
          <div><ThemeSwitcher /></div>
      </header>
    );
  };
