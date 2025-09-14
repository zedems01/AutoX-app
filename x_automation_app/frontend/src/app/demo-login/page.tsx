"use client"

import { useMutation } from "@tanstack/react-query"
import { useRouter, useSearchParams } from "next/navigation"
import { toast } from "sonner"
import { Loader2, ShieldCheck, ShieldX } from "lucide-react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { demoLogin } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"

export default function DemoLoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login: authLogin } = useAuth()
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const tokenFromUrl = searchParams.get('token')
    if (tokenFromUrl) {
      setToken(tokenFromUrl)
    }
  }, [searchParams])

  const mutation = useMutation({
    mutationFn: (token: string) => demoLogin(token),
    onSuccess: (data) => {
      toast.success("Login successful!", { duration: 5000 })
      authLogin(data)
      router.push("/")
    },
    onError: (error) => {
      toast.error(`Demo login failed: ${error.message}`, {
        duration: 15000,
      })
    },
  })

  function handleDemoLogin() {
    if (token) {
      mutation.mutate(token)
    }
  }

  if (!token) {
    return (
      <div className="flex justify-center pt-20">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto bg-destructive/10 w-fit p-3 rounded-lg mb-4">
              <ShieldX className="h-10 w-10 text-destructive" />
            </div>
            <CardTitle>Access Denied</CardTitle>
            <CardDescription>
              This demo link is invalid or incomplete. Please use the link
              provided by the administrator.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex justify-center pt-20">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto bg-primary/10 w-fit p-3 rounded-lg mb-4">
            <ShieldCheck className="h-10 w-10 text-primary" />
          </div>
          <CardTitle>AutoX Workflow Demo</CardTitle>
          <CardDescription>
            Click the button below to log in with a demo account and try out the
            automated workflow.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleDemoLogin}
            className="w-full cursor-pointer"
            disabled={mutation.isPending || !token}
          >
            {mutation.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            Access Demo
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
