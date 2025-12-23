"use client";

import React, { createContext, useContext } from "react";

type AdminContextType = {
  isAdmin: boolean;
};

const AdminContext = createContext<AdminContextType>({ isAdmin: false });

export const AdminProvider = ({
  isAdmin = false,
  children,
}: {
  isAdmin?: boolean;
  children: React.ReactNode;
}) => {
  return <AdminContext.Provider value={{ isAdmin }}>{children}</AdminContext.Provider>;
};

export const useAdmin = (): AdminContextType => {
  return useContext(AdminContext);
};