Group {
    <region:group>

    domain = Region[{<name:region>}];

    roi = Region[{<name:roi>}];
    source = Region[{<tag:source>}];
    sink = Region[{<tag:sink>}];

    dom_active = Region[{source, sink}];
}

Function {
    <name:sigma>

    unit_current[source] = 1;
    unit_current[sink] = -1;
}

FunctionSpace {
    {
        Name function_space; Type Form0;
        BasisFunction {
            {
                Name sn; NameOfCoef vn; Function BF_Node;
                Support Region[{domain, dom_active}]; Entity NodesOf[All];
            }
        }
    }
}

Jacobian {
    {
        Name jacobian;
        Case {
            {
                Region All; Jacobian Vol;
            }
        }
    }
    {
        Name jacobian_sur;
        Case {
            {
                Region All; Jacobian Sur;
            }
        }
    }
    {
        Name jacobian_lin;
        Case {
            {
                Region All; Jacobian Lin;
            }
        }
    }
}

Integration {
    {
        Name integration;
        Case {
            {
                Type Gauss;
                Case {
                    {
                        GeoElement Triangle; NumberOfPoints  1;
                    }
                    {
                        GeoElement Tetrahedron  ; NumberOfPoints  1;
                    }
                    {
                        GeoElement Line; NumberOfPoints 1;
                    }
                    {
                        GeoElement Point; NumberOfPoints 1;
                    }
                }
            }
        }
    }
}

Formulation {
    {
        Name formulation; Type FemEquation;
        Quantity {
            {
                Name v; Type Local; NameOfSpace function_space;
            }
        }
        Equation {
            Integral {
                [sigma[] * Dof{ d v } , { d v }];
                In domain; Jacobian jacobian; Integration integration;
            }
            Integral {
                [-unit_current[] , { v }];
                In dom_active; Jacobian jacobian; Integration integration;
            }
        }
    }
}

Function {
    For i_sensor In {0:<count:sensors>}
        b_path = Sprintf["%g.b", i_sensor];
        b~{i_sensor}() = ListFromFile[b_path];
    EndFor
}

Resolution {
    {
        Name resolution;
        System {
            {
                Name system; NameOfFormulation formulation;
            }
        }
        Operation {
            Generate[system];
            For i_sensor In {0:<count:sensors>}
                Evaluate[ $i_solution = i_sensor ];
                CopyRHS[b~{i_sensor}(), system];
                SolveAgain[system];
                SaveSolution[system];
                PostOperation[post_operation];
            EndFor
        }
    }
}

PostProcessing {
    {
        Name post_processing; NameOfFormulation formulation;
        Quantity {
            {
                Name v;
                Value {
                    Term {
                        [{ v }]; In domain; Jacobian jacobian;
                    }
                }
            }
            {
                Name e;
                Value {
                    Term {
                        [-{ d v }]; In domain; Jacobian jacobian;
                    }
                }
            }
            /*{
                Name j;
                Value {
                    Term {
                        [-sigma[] * { d v }]; In domain; Jacobian jacobian;
                    }
                }
            }*/
        }
    }
}

PostOperation {
    {
        Name post_operation; NameOfPostProcessing post_processing;
        Operation {
            Print[e, OnElementsOf roi, Format Table,
                  File "", AppendExpressionToFileName $i_solution,
                  AppendStringToFileName ".e"];
        }
    }
}
