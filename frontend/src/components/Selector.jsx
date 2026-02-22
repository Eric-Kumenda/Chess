// import React from "react";
// import { useDispatch, useSelector } from "react-redux";
// import { selectSide } from "../store/gameSlice";
// import { CButton, CNav, CNavItem, CNavLink } from "@coreui/react";

// const Selector = () => {
//   const dispatch = useDispatch();

//   const sideSelected = useSelector((state) => state.game.sideSelection);
//   const status = useSelector((state) => state.game.status);

//   const handleClick = (val) => {
//     dispatch(selectSide(val));
//   };

//   return (
//     <CNav variant="enclosed">
//       <CNavItem>
//         <CNavLink
//           className="d-inline-flex"
//           as={CButton}
//           active={sideSelected === "X"}
//           onClick={() => handleClick("X")}
//           disabled={status!=='Inactive'}
//         >
//           X
//         </CNavLink>
//         <CNavLink
//           className="d-inline-flex"
//           as={CButton}
//           active={sideSelected === "O"}
//           onClick={() => handleClick("O")}
//           disabled={status!=='Inactive'}
//         >
//           O
//         </CNavLink>
//       </CNavItem>
//     </CNav>
//   );
// };

// export default Selector;
