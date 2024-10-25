// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

export const LightboxButton = ({ onClick, children, className = '' }) => {
  return (
    <div
      onClick={onClick}
      className={`flex cursor-pointer items-center justify-center rounded-full
        p-2 text-white transition-colors duration-700 ease-in-out
        hover:bg-custom-dark-4 ${className}`}>
      {children}
    </div>
  );
};
