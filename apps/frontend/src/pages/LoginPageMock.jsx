import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { FormField } from "../components/common/FormField";
import { PageContainer } from "../components/common/pageContainer";

export default function LoginPageMock() {
  return (
    <PageContainer>
      <div className="mx-auto max-w-md">
        <Card>
          <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>
              Página mockada baseada na estética do frontend anexado.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <FormField label="E-mail">
              <Input placeholder="Digite seu e-mail" />
            </FormField>

            <FormField label="Senha">
              <Input type="password" placeholder="Digite sua senha" />
            </FormField>

            <Button>Entrar</Button>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}