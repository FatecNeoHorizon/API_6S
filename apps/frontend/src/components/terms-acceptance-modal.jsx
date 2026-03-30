"use client";

import { useState } from "react";
import { Check, AlertTriangle, ScrollText } from "lucide-react";
import PropTypes from "prop-types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function TermsAcceptanceModal({ terms, onAccept }) {
  const [acceptedTerms, setAcceptedTerms] = useState({});
  const [expandedTerm, setExpandedTerm] = useState(null);
  const [readTerms, setReadTerms] = useState({});

  const allRequiredAccepted = terms
    .filter((t) => t.required)
    .every((t) => acceptedTerms[t.id]);

  const handleToggleTerm = (termId) => {
    if (!readTerms[termId]) return;
    setAcceptedTerms((prev) => ({
      ...prev,
      [termId]: !prev[termId],
    }));
  };

  const handleExpandTerm = (termId) => {
    setExpandedTerm(expandedTerm === termId ? null : termId);
    setReadTerms((prev) => ({
      ...prev,
      [termId]: true,
    }));
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case "uso":
        return "Termos de Uso";
      case "lgpd":
        return "Politica LGPD";
      case "privacidade":
        return "Politica de Privacidade";
      default:
        return type;
    }
  };

  const getCheckboxClassName = (termId) => {
    if (acceptedTerms[termId]) return "bg-primary border-primary";
    if (readTerms[termId]) return "border-border hover:border-primary";
    return "border-border/50 cursor-not-allowed";
  };

  const getTypeColor = (type) => {
    switch (type) {
      case "uso":
        return "bg-chart-1/20 text-chart-1";
      case "lgpd":
        return "bg-chart-2/20 text-chart-2";
      case "privacidade":
        return "bg-chart-3/20 text-chart-3";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/90 backdrop-blur-sm p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col border-border bg-card">
        <CardHeader className="border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <ScrollText className="w-6 h-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl text-foreground">
                Aceite de Termos
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Para continuar, voce precisa aceitar os termos abaixo
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center gap-2 p-3 bg-chart-3/10 border border-chart-3/20 rounded-lg mb-4">
            <AlertTriangle className="w-5 h-5 text-chart-3 shrink-0" />
            <p className="text-sm text-foreground">
              Primeiro acesso detectado. Por favor, leia e aceite os termos para
              continuar usando a plataforma.
            </p>
          </div>

          <div className="flex flex-col gap-3">
            {terms.map((term) => (
              <div
                key={term.id}
                className="border border-border rounded-lg overflow-hidden bg-secondary/30"
              >
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleToggleTerm(term.id)}
                      disabled={!readTerms[term.id]}
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${getCheckboxClassName(term.id)}`}
                    >
                      {acceptedTerms[term.id] && (
                        <Check className="w-3 h-3 text-primary-foreground" />
                      )}
                    </button>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-foreground">
                          {term.title}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${getTypeColor(term.type)}`}
                        >
                          {getTypeLabel(term.type)}
                        </span>
                        {term.required && (
                          <span className="text-xs text-destructive">
                            *Obrigatorio
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        Versao {term.version}
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleExpandTerm(term.id)}
                    className="text-primary hover:text-primary"
                  >
                    {expandedTerm === term.id ? "Fechar" : "Ler Termo"}
                  </Button>
                </div>

                {expandedTerm === term.id && (
                  <div className="border-t border-border p-4 bg-background/50">
                    <div className="prose prose-sm prose-invert max-w-none">
                      <div className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                        {term.content}
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-border flex justify-end">
                      <Button
                        size="sm"
                        onClick={() => {
                          setAcceptedTerms((prev) => ({
                            ...prev,
                            [term.id]: true,
                          }));
                          setExpandedTerm(null);
                        }}
                        className="bg-primary text-primary-foreground hover:bg-primary/90"
                      >
                        <Check className="w-4 h-4 mr-2" />
                        Li e Aceito
                      </Button>
                    </div>
                  </div>
                )}

                {!readTerms[term.id] && !expandedTerm && (
                  <div className="px-4 pb-3">
                    <p className="text-xs text-muted-foreground">
                      Clique em "Ler Termo" para habilitar o aceite
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>

        <div className="border-t border-border p-4 bg-card">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {Object.values(acceptedTerms).filter(Boolean).length} de{" "}
              {terms.length} termos aceitos
            </p>
            <Button
              onClick={onAccept}
              disabled={!allRequiredAccepted}
              className="bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              Continuar para o Sistema
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

TermsAcceptanceModal.propTypes = {
  terms: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      type: PropTypes.oneOf(["uso", "lgpd", "privacidade"]).isRequired,
      version: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      required: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  onAccept: PropTypes.func.isRequired,
};
