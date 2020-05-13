Group {
    // Head
    <tissues:region>

    Dom_Head = Region[{<tissues:name>}];

    // Sources
    <sources:region>

    Dom_Sources = Region[{<sources:name>}];

    // All
    Dom_All = Region[{Dom_Head, Dom_Sources}];
}

Function {
    // Electrical conductivity [S/m]
    <tissues:sigma>

    // Current [A]
    <sources:current>
}

FunctionSpace {
    {
        Name FuncSp_v; Type Form0;
        BasisFunction {
            {
                Name BasFunc_v; NameOfCoef Coef_v; Function BF_Node;
                Support Dom_All; Entity NodesOf[All];
            }
        }
    }
}

Jacobian {
    {
        Name Jac_Vol;
        Case {
            { Region All; Jacobian Vol; }
        }
    }
    {
        Name Jac_Sur;
        Case {
            { Region All; Jacobian Sur; }
        }
    }
    {
        Name Jac_Lin;
        Case {
            { Region All; Jacobian Lin; }
        }
    }
}

Integration {
    {
        Name Int;
        Case {
            {
                Type Gauss;
                Case {
                    { GeoElement Triangle; NumberOfPoints  1; }
                    { GeoElement Tetrahedron  ; NumberOfPoints  1; }
                    { GeoElement Line; NumberOfPoints 1; }
                    { GeoElement Point; NumberOfPoints 1; }
                }
            }
        }
    }
}

Formulation {
    {
        Name Form_v; Type FemEquation;
        Quantity {
            { Name v; Type Local; NameOfSpace FuncSp_v; }
        }
        Equation {
            Integral {
                [sigma[] * Dof{d v}, {d v}];
                In Dom_Head; Jacobian Jac_Vol;
                Integration Int;
            }
            Integral {
                [-current[], {v}];
                In Dom_Sources; Jacobian Jac_Vol; Integration Int;
            }
        }
    }
}

Resolution {
    {
        Name Res_v;
        System {
            { Name Sys_v; NameOfFormulation Form_v; }
        }
        Operation {
            Generate[Sys_v];
            Solve[Sys_v];
            SaveSolution[Sys_v];
        }
    }
}

PostProcessing {
    {
        Name PostPro_v; NameOfFormulation Form_v;
        Quantity {
            {
                Name v;
                Value {
                    Term { [{v}]; In Dom_Head; Jacobian Jac_Vol; }
                }
            }
            {
                Name j;
                Value {
                    Term { [-sigma[] * {d v}]; In Dom_Head; Jacobian Jac_Vol; }
                }
            }
        }
    }
}

PostOperation {
    {
        Name PostOp_v; NameOfPostProcessing PostPro_v;
        Operation {
            Print[j, OnElementsOf Dom_Head, File "j.pos"];
            Print[v, OnElementsOf Dom_Head, File "v.pos"];
            Print[v, OnElementsOf Dom_Head, Skin, File "v_skin.pos"];
            Print[v, OnElementsOf Dom_Head, Skin, Format NodeTable, File "v_skin.node"];
        }
    }
}
