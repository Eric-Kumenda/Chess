import React, { useEffect, useState } from "react";
import "./theme.css";
import { useColorModes } from "@coreui/react";
import { useDispatch, useSelector } from "react-redux";
import { setTheme } from "../../store/themeSlice";

const ThemeSwitch = () => {
  const dispatch = useDispatch();

  const { colorMode, setColorMode } = useColorModes("Chessy");
  dispatch(setTheme(colorMode));
  const storedTheme = useSelector((state) => state.theme.theme);
  const [checkBoxState, setCheckBoxState] = useState(storedTheme);

  useEffect(() => {
    if (storedTheme) {
      setCheckBoxState(storedTheme);
    }
    console.log(storedTheme);
  }, [storedTheme]);

  const handleToggle = () => {
    const newTheme = colorMode === "light" ? "dark" : "light";
    setColorMode(newTheme);
    dispatch(setTheme(newTheme));
  };
  return (
      <input
        type="checkbox"
        className="theme-checkbox"
        key={`themeChanger${checkBoxState}`}
        checked={checkBoxState === "dark"}
        onClick={handleToggle}
        onChange={(e) => e.preventDefault()}
      />
  );
};

export default ThemeSwitch;
