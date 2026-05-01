"use client";


import FileUploadUI from "./FileUploadUI";
import UploadModal from "./uploadmodel/UploadModal";
import { useState, useEffect, useRef } from "react";

interface Props {
  collapsed?: boolean;
  onFileSelect: (file: File) => void;
  autoOpen?: boolean;
}

const FileUpload: React.FC<Props> = ({
  collapsed,
  onFileSelect,
  autoOpen
}) => {
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleFile = (file: File) => {
    onFileSelect(file);
  };
const hasAutoOpened = useRef(false);

useEffect(() => {
  if (autoOpen && !hasAutoOpened.current) {
    hasAutoOpened.current = true;

    setTimeout(() => {
      setOpen(true);
    }, 0);
  }
}, [autoOpen]);

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