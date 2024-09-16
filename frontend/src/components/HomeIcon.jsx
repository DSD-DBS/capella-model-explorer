// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { Home } from 'lucide-react';
import { Link } from 'react-router-dom';

export const HomeIcon = () => {
  return (
    <Link to="/">
      <div className="header-button">
        <Home className="h-6 w-6 text-white" />
      </div>
    </Link>
  );
};
