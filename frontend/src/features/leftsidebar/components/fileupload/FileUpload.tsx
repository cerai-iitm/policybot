"use client";

import { useState } from "react";
import FileUploadUI from "./FileUploadUI";
import UploadModal from "./uploadmodel/UploadModal";

interface Props {
  collapsed?: boolean;
  onFileSelect: (file: File) => void;
}

const FileUpload: React.FC<Props> = ({
  collapsed,
  onFileSelect,
}) => {
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleFile = (file: File) => {
    onFileSelect(file);
  };

  return (
    <>
      <FileUploadUI
        collapsed={collapsed}
        onClick={handleOpen}
      />

      <UploadModal
        open={open}
        onClose={handleClose}
        onFileSelect={handleFile}
      />
    </>
  );
};

export default FileUpload;