import { useState, useEffect } from "react";
import "./App.css";
import { useDispatch, useSelector } from "react-redux";
import {
  CCol,
  CButton,
  CContainer,
  CNavbar,
  CNavLink,
  CRow,
  useColorModes,
  CNav,
  CNavItem,
  CTooltip,
  CAvatar,
  CFormSelect,
} from "@coreui/react";
import ThemeSwitch from "./components/theme/ThemeSwitch";
import ChessBoard from "./components/ChessBoard";
import { setSelectedModel, setUserColor } from "./store/chessSlice";

function App() {
  const dispatch = useDispatch();

  const { isColorModeSet, setColorMode } = useColorModes("Chessy");
  const storedTheme = useSelector((state) => state.theme.theme);
  const userColor = useSelector((state) => state.chess.userColor);

  const handleModelChange = (event) => {
    const selectedModel = event.target.value;
    dispatch(setSelectedModel(selectedModel));
  };
  const handleColorSelect = (color) => {
    userColor !== color && dispatch(setUserColor(color));
  };

  const models = [
    {
      title: "Minimax",
      description:
        "Minimax is a recursive algorithm used for decision making in games like chess.",
    } /*
    {
      title: "Alpha-Beta Pruning",
      description:
        "Alpha-Beta Pruning is an optimization over the standard minimax algorithm for decision making in games like chess.",
    },
    {
      title: "Monte Carlo Tree Search",
      description:
        "Monte Carlo Tree Search  is a heuristic search algorithm used for decision making in games like chess.",
    },*/,
    {
      title: "CNN1 + VTT Evaluation",
      description:
        "CNN Evaluation is a method used for decision making in games like chess.",
    },
    {
      title: "CNN2 Evaluation",
      description:
        "CNN + VTT Evaluation is a method used for decision making in games like chess.",
    },
    {
      title: "Stockfish",
      description: "Stockfish is a free and open-source chess engine.",
    },
  ]; // useEffect(() => {
  //   const urlParams = new URLSearchParams(window.location.href.split('?')[1])
  //   const theme = urlParams.get('theme') && urlParams.get('theme').match(/^[A-Za-z0-9\s]+/)[0]
  //   if (theme) {
  //     setColorMode(theme)
  //   }

  //   if (isColorModeSet()) {
  //     return
  //   }

  //   // setColorMode(storedTheme)
  // }, [])
  // const sessionId = useSelector((state) => state.game.sessionId);
  // const sessionStatus = useSelector((state) => state.game.status);
  return (
    <>
      <CContainer className="pt-1 px-2 h-100 pb-5 pb-md-1 mb-5 mb-md-2" xxl>
        <CRow className="h-100 ">
          <CCol
            xs={12}
            md={4}
            className="border-end border-1 border-secondary d-none d-md-block"
          >
            <CRow className="justify-content-center pt-5">
              <CAvatar
                className="img-fluid"
                style={{ height: "200px", width: "200px" }}
                src="https://images.unsplash.com/photo-1560174038-da43ac74f01b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2hlc3N8ZW58MHx8MHx8fDA%3D"
              />
            </CRow>
            <CRow className="justify-content-center py-2">
              <span className="fw-bold text-center">
                Blitz with AI in the style of Magnus C.
              </span>
            </CRow>
            <CRow className="py-2">
              <CCol className="d-flex justify-content-center gap-1">
                <CButton className="btn-sm btn-outline-secondary">Easy</CButton>
                <CButton className="btn-sm btn-secondary">Medium</CButton>
                <CButton className="btn-sm btn-outline-secondary">Hard</CButton>
              </CCol>
            </CRow>
            <CRow className="py-2">
              <CCol className="d-flex justify-content-center gap-1">
                <CButton className="btn-sm btn-outline-secondary">
                  3 min.
                </CButton>
                <CButton className="btn-sm btn-secondary">5 min.</CButton>
                <CButton className="btn-sm btn-outline-secondary">
                  10 min.
                </CButton>
              </CCol>
            </CRow>
            <CRow className="py-2">
              <CCol className="d-flex justify-content-center gap-1">
                <CButton
                  className="btn-sm btn-secondary fs-6"
                  onClick={() => handleColorSelect("w")}
                >
                  <i className="fa-solid text-white fa-chess-pawn me-2"></i>{" "}
                  White
                </CButton>
                <CButton
                  className="btn-sm btn-outline-secondary fs-6"
                  onClick={() => handleColorSelect("b")}
                >
                  <i className="fa-solid text-black fa-chess-pawn me-2"></i>{" "}
                  Black
                </CButton>
              </CCol>
            </CRow>
            <CRow className="py-2">
              <CCol className="d-flex justify-content-center ">
                <CTooltip content="Select AI bot" placement="top">
                  <CFormSelect
                    aria-label="Ai Bot"
                    className="w-auto"
                    onChange={handleModelChange}
                  >
                    {models.map((model) => {
                      return (
                        <option key={model.title} value={model.title}>
                          {model.title}
                        </option>
                      );
                    })}
                  </CFormSelect>
                </CTooltip>
              </CCol>
            </CRow>
            <CRow className="py-2">
              <CCol className="d-flex justify-content-center ">
                <CTooltip content="Start/Pause Game" placement="top">
                  <CButton className="btn-secondary ">Start</CButton>
                </CTooltip>
              </CCol>
            </CRow>
          </CCol>
          <CCol xs={12} md={8}>
            {/* <CRow className="justify-content-end">
              <CCol className="col-auto">
                <ThemeSwitch />
              </CCol>
            </CRow> */}
            {/* <CRow className="justify-content-center pt-2">
              <CCol className="col-auto"> <Selector /> </CCol>
            </CRow> */}
            <CRow className="align-items-center h-100 pt-5">
              <CCol className="col-md-8 col-lg-6 d-flex mx-auto justify-content-center align-items-center m-h-100">
                <ChessBoard />
              </CCol>
            </CRow>
          </CCol>
        </CRow>
        <CNavbar className="bg-body-secondary" placement="fixed-bottom">
          <CContainer fluid>
            <CNav
              variant="enclosed"
              className="w-100 d-flex justify-content-around rounded-0 bg-transparent"
            >
              <CNavItem>
                <CTooltip content="Game" placement="top">
                  <CNavLink as={CButton} href="#" active>
                    <i className="fa-solid fa-dice"></i>
                    <p className="d-md-none p-0 m-0">Game</p>
                  </CNavLink>
                </CTooltip>
              </CNavItem>
              <CNavItem>
                <CTooltip content="Stats" placement="top">
                  <CNavLink as={CButton} href="#">
                    <i className="fa-solid fa-chart-column"></i>
                    <p className="d-md-none p-0 m-0">Stats</p>
                  </CNavLink>
                </CTooltip>
              </CNavItem>
              <CNavItem>
                <CTooltip content="Info" placement="top">
                  <CNavLink as={CButton} href="#">
                    <i className="fa-regular fa-circle-info"></i>
                    <p className="d-md-none p-0 m-0">Info</p>
                  </CNavLink>
                </CTooltip>
              </CNavItem>
              <CNavItem>
                <CTooltip content="Theme" placement="top">
                  <CNavLink as={CButton} href="#">
                    <i className="fa-solid fa-sun-bright"></i>
                    <p className="d-md-none p-0 m-0">Theme</p>
                  </CNavLink>
                </CTooltip>
              </CNavItem>
            </CNav>
          </CContainer>
        </CNavbar>
      </CContainer>
    </>
  );
}

export default App;
