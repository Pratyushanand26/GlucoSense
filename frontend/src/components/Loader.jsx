import React from "react";

const Loader = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col justify-center items-center h-full py-10 text-blue-600">
      <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p className="mt-3 font-medium">{message}</p>
    </div>
  );
};

export default Loader;
