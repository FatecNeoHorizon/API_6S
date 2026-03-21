import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { FormField } from "../components/common/FormField";
import { PageContainer } from "../components/common/pageContainer";

export default function PrimeiroAcessoPageMock() {
  return (
    <PageContainer>
      <div className="mx-auto max-w-lg">
        <Card>
          <CardHeader>
            <CardTitle>Primeiro Acesso</CardTitle>
            <CardDescription>
              Estrutura inicial para futura substituição pela página real.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <FormField label="Nova senha">
              <Input type="password" placeholder="Digite a nova senha" />
            </FormField>

            <FormField label="Confirmar senha">
              <Input type="password" placeholder="Confirme a nova senha" />
            </FormField>

            <Button>Continuar</Button>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}